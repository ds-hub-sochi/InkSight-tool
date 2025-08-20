import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
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
from ..core.auth import get_current_active_user

router = APIRouter()

chatbot: AgenticChatBot = None
data_pipeline: DataPreparationPipeline = None
file_processor: FileProcessor = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatMessage, current_user: dict = Depends(get_current_active_user)):
    if not chatbot:
        raise HTTPException(status_code=500, detail="Service unavailable")
    try:
        response = chatbot.chat(request.message)
        result = ChatResponse(response=response)
        if request.include_sources:
            kb_info = chatbot.search_knowledge_base(request.message)
            if "results" in kb_info:
                result.sources = kb_info["results"]
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to process your request. Please try again.")


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest, current_user: dict = Depends(get_current_active_user)):
    if not chatbot:
        raise HTTPException(status_code=500, detail="Service unavailable")
    try:
        results = chatbot.search_knowledge_base(query=request.query, k=request.k)
        if "error" in results:
            raise HTTPException(status_code=400, detail="Search failed")
        return SearchResponse(**results)
    except Exception:
        raise HTTPException(status_code=500, detail="Search unavailable. Please try again.")


@router.post("/process-documents", response_model=ProcessDocumentsResponse)
async def process_documents(request: ProcessDocumentsRequest, current_user: dict = Depends(get_current_active_user)):
    if not data_pipeline:
        raise HTTPException(status_code=500, detail="Service unavailable")
    if not os.path.exists(request.documents_path):
        raise HTTPException(status_code=400, detail="Documents path does not exist")
    try:
        chunks_processed = data_pipeline.process_documents(
            documents_path=request.documents_path,
            clear_existing=request.clear_existing,
        )
        return ProcessDocumentsResponse(
            success=True,
            message=f"Successfully processed documents from {request.documents_path}",
            chunks_processed=chunks_processed,
        )
    except Exception:
        return ProcessDocumentsResponse(
            success=False,
            message="Error processing documents. Please try again.",
            chunks_processed=0,
        )


@router.get("/store-info", response_model=StoreInfoResponse)
async def get_store_info():
    if not chatbot:
        raise HTTPException(status_code=500, detail="Service unavailable")
    try:
        info = chatbot.get_knowledge_base_info()
        store_ready = chatbot.retrieval_service.is_store_ready()
        return StoreInfoResponse(
            document_count=info.get("document_count", 0),
            reranker_enabled=info.get("reranker_enabled", False),
            reranker_model=info.get("reranker_model"),
            store_ready=store_ready,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Store information unavailable")


@router.delete("/clear-memory")
async def clear_memory(current_user: dict = Depends(get_current_active_user)):
    if not chatbot:
        raise HTTPException(status_code=500, detail="Service unavailable")
    try:
        chatbot.clear_memory()
        return JSONResponse(content={"message": "Memory cleared successfully"})
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to clear memory")


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_active_user)):
    if not data_pipeline or not file_processor:
        raise HTTPException(status_code=500, detail="Service unavailable")
    if not FileProcessor.is_supported_file(file.filename):
        supported = FileProcessor.get_supported_extensions()
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Supported types: {', '.join(supported)}")
    try:
        file_bytes = await file.read()
        documents, file_info = file_processor.process_uploaded_file(
            file_bytes=file_bytes,
            filename=file.filename,
            metadata={"upload_source": "api"},
        )
        text_chunker = TextChunker()
        chunks = text_chunker.chunk_documents(documents)
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
    except Exception:
        return UploadDocumentResponse(
            success=False,
            message="Error processing file. Please try again.",
            filename=file.filename or "unknown",
            chunks_processed=0,
            file_size_bytes=0,
        )


@router.get("/supported-formats")
async def get_supported_formats():
    return JSONResponse(content={
        "supported_extensions": FileProcessor.get_supported_extensions(),
        "max_file_size_mb": FileProcessor.MAX_FILE_SIZE / (1024 * 1024),
    })


@router.get("/health")
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "chatbot_ready": chatbot is not None,
        "data_pipeline_ready": data_pipeline is not None,
        "file_processor_ready": file_processor is not None,
    })
