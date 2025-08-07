from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""

    message: str = Field(..., description="The user message")
    include_sources: bool = Field(
        default=False,
        description="Whether to include source documents in response"
    )


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str = Field(..., description="The chatbot response")
    sources: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Source documents if requested"
    )


class SearchRequest(BaseModel):
    """Knowledge base search request."""

    query: str = Field(..., description="Search query")
    k: int = Field(default=4, ge=1, le=20,
                   description="Number of results to return")
    include_scores: bool = Field(
        default=False, description="Whether to include similarity scores"
    )


class SearchResponse(BaseModel):
    """Knowledge base search response."""

    query: str
    results: List[Dict[str, Any]]


class ProcessDocumentsRequest(BaseModel):
    """Request to process documents."""

    documents_path: str = Field(..., description="Path to documents directory")
    clear_existing: bool = Field(
        default=False, description="Whether to clear existing vector store"
    )


class ProcessDocumentsResponse(BaseModel):
    """Response from document processing."""

    success: bool
    message: str
    chunks_processed: int


class StoreInfoResponse(BaseModel):
    """Vector store information response."""

    document_count: int
    reranker_enabled: bool
    reranker_model: Optional[str]
    store_ready: bool


class UploadDocumentResponse(BaseModel):
    """Response from document upload."""

    success: bool
    message: str
    filename: str
    chunks_processed: int
    file_size_bytes: int
