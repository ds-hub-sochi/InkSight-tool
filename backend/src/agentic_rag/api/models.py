from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


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


# Authentication Models
class UserCreate(BaseModel):
    """User creation model."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class UserLogin(BaseModel):
    """User login model."""
    
    username: str
    password: str


class User(BaseModel):
    """User model."""
    
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """JWT token response."""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    
    username: Optional[str] = None
