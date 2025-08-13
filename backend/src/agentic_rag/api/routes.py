import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse

from .models import (
    ChatMessage,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    ProcessDocumentsRequest,
    ProcessDocumentsResponse,
    StoreInfoResponse,
    UploadDocumentResponse,
)
from ..services.agent import AgenticChatBot
from ..services.data_pipeline import DataPreparationPipeline
from ..services.file_processor import FileProcessor
from ..services.text_splitter import TextChunker

router = APIRouter()

# Global instances (will be initialized in main.py)
chatbot: AgenticChatBot = None
data_pipeline: DataPreparationPipeline = None
file_processor: FileProcessor = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatMessage):
    """Chat with the agentic RAG bot."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    try:
        response = chatbot.chat(request.message)

        result = ChatResponse(response=response)

        # Optionally include source documents
        if request.include_sources:
            # Extract the last search results if available
            kb_info = chatbot.search_knowledge_base(
                request.message, include_scores=True
            )
            if "results" in kb_info:
                result.sources = kb_info["results"]

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest):
    """Search the knowledge base directly."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    try:
        results = chatbot.search_knowledge_base(
            query=request.query, k=request.k
        )

        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])

        return SearchResponse(**results)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching knowledge base: {str(e)}"
        )


@router.post("/process-documents", response_model=ProcessDocumentsResponse)
async def process_documents(
    request: ProcessDocumentsRequest, background_tasks: BackgroundTasks
):
    """Process documents and add them to the vector store."""
    if not data_pipeline:
        raise HTTPException(status_code=500, detail="Data pipeline not initialized")

    if not os.path.exists(request.documents_path):
        raise HTTPException(
            status_code=400,
            detail=f"Documents path does not exist: {request.documents_path}",
        )

    try:
        # Run processing in background
        def process_docs():
            return data_pipeline.process_documents(
                documents_path=request.documents_path,
                clear_existing=request.clear_existing,
            )

        chunks_processed = process_docs()

        return ProcessDocumentsResponse(
            success=True,
            message=f"Successfully processed documents from {request.documents_path}",
            chunks_processed=chunks_processed,
        )

    except Exception as e:
        return ProcessDocumentsResponse(
            success=False,
            message=f"Error processing documents: {str(e)}",
            chunks_processed=0,
        )


@router.get("/store-info", response_model=StoreInfoResponse)
async def get_store_info():
    """Get information about the vector store."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    try:
        info = chatbot.get_knowledge_base_info()
        store_ready = chatbot.retrieval_service.is_store_ready()

        return StoreInfoResponse(
            document_count=info.get("document_count", 0),
            reranker_enabled=info.get("reranker_enabled", False),
            reranker_model=info.get("reranker_model"),
            store_ready=store_ready,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting store info: {str(e)}"
        )


@router.delete("/clear-memory")
async def clear_memory():
    """Clear the chatbot's conversation memory."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    try:
        chatbot.clear_memory()
        return JSONResponse(content={"message": "Memory cleared successfully"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document file."""
    if not data_pipeline or not file_processor:
        raise HTTPException(status_code=500, detail="Services not initialized")

    # Validate file type
    if not FileProcessor.is_supported_file(file.filename):
        supported = FileProcessor.get_supported_extensions()
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {', '.join(supported)}",
        )

    try:
        # Read file bytes
        file_bytes = await file.read()

        # Process the uploaded file
        documents, file_info = file_processor.process_uploaded_file(
            file_bytes=file_bytes,
            filename=file.filename,
            metadata={"upload_source": "api"},
        )

        # Chunk the documents
        text_chunker = TextChunker()
        chunks = text_chunker.chunk_documents(documents)

        # Add to vector store
        data_pipeline.vector_store.initialize_store()
        data_pipeline.vector_store.add_documents(chunks)

        return UploadDocumentResponse(
            success=True,
            message=f"Successfully processed and uploaded {file.filename}",
            filename=file.filename,
            chunks_processed=len(chunks),
            file_size_bytes=file_info["size_bytes"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return UploadDocumentResponse(
            success=False,
            message=f"Error processing file: {str(e)}",
            filename=file.filename or "unknown",
            chunks_processed=0,
            file_size_bytes=0,
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats."""
    return JSONResponse(
        content={
            "supported_extensions": FileProcessor.get_supported_extensions(),
            "max_file_size_mb": FileProcessor.MAX_FILE_SIZE / (1024 * 1024),
        }
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "chatbot_ready": chatbot is not None,
            "data_pipeline_ready": data_pipeline is not None,
            "file_processor_ready": file_processor is not None,
        }
    )
