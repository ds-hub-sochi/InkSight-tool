import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agentic_rag.core.config import settings
from src.agentic_rag.services.agent import AgenticChatBot
from src.agentic_rag.services.data_pipeline import DataPreparationPipeline
from src.agentic_rag.services.file_processor import FileProcessor
from src.agentic_rag.api import routes


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        description="Agentic RAG System with Vector Search and LLM Chat",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(routes.router, prefix="/api/v1")

    return app


def initialize_services():
    """Initialize the chatbot and data pipeline services."""

    # Create necessary directories
    Path(settings.vector_store_path).mkdir(parents=True, exist_ok=True)
    Path(settings.documents_path).mkdir(parents=True, exist_ok=True)

    # Initialize data pipeline
    routes.data_pipeline = DataPreparationPipeline(
        vector_store_path=settings.vector_store_path,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        embedding_model=settings.embedding_model,
    )

    # Initialize chatbot
    routes.chatbot = AgenticChatBot(
        model_name=settings.model_name,
        vector_store_path=settings.vector_store_path,
        enable_reranker=settings.enable_reranker,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        memory_window=settings.memory_window,
        langsmith_project=settings.langsmith_project,
    )

    # Initialize file processor
    routes.file_processor = FileProcessor()

    print("Services initialized successfully")
    print(f"Vector store: {settings.vector_store_path}")
    print(f"Documents path: {settings.documents_path}")
    print(f"Model: {settings.model_name}")
    print(f"Reranker enabled: {settings.enable_reranker}")
    print(f"File upload: {FileProcessor.MAX_FILE_SIZE / (1024*1024):.0f}MB")


def process_existing_documents():
    """Process any existing documents in the documents directory."""
    docs_path = Path(settings.documents_path)

    if not docs_path.exists():
        return

    # Check if there are any documents to process
    supported_files = list(docs_path.glob("*.txt")) + list(docs_path.glob("*.pdf"))

    if supported_files:
        print(f"Found {len(supported_files)} document(s) to process...")

        try:
            chunks_processed = routes.data_pipeline.process_documents(
                documents_path=str(docs_path), clear_existing=False
            )
            print(f"Processed {chunks_processed} document chunks")
        except Exception as e:
            print(f"Error processing documents: {e}")
    else:
        print(f"No documents found in {docs_path}")


# Create the FastAPI app
app = create_app()


@app.on_event("startup")
async def startup_event():
    """Initialize services when the app starts."""
    print("🚀 Starting Agentic RAG System...")

    # Initialize services
    initialize_services()

    # Process any existing documents
    process_existing_documents()

    print("✅ System ready!")


@app.get("/")
async def root():
    """Root endpoint with system information."""
    store_info = routes.chatbot.get_knowledge_base_info() if routes.chatbot else {}

    return {
        "message": "Agentic RAG System API",
        "version": settings.app_version,
        "endpoints": {
            "chat": "/api/v1/chat",
            "search": "/api/v1/search",
            "upload": "/api/v1/upload",
            "process_documents": "/api/v1/process-documents",
            "store_info": "/api/v1/store-info",
            "clear_memory": "/api/v1/clear-memory",
            "supported_formats": "/api/v1/supported-formats",
            "health": "/api/v1/health",
        },
        "knowledge_base": store_info,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
