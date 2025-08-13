from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    app_name: str = Field(default="Agentic RAG System")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    # OpenRouter Settings
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    model_name: str = Field(default="anthropic/claude-3-5-sonnet")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)

    # LangSmith Settings
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    langsmith_project: Optional[str] = Field(default=None, env="LANGCHAIN_PROJECT")

    # Vector Store Settings
    vector_store_path: str = Field(default="./vector_store")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    # Document Processing Settings
    documents_path: str = Field(default="./documents")
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=200, ge=0)

    # Retrieval Settings
    enable_reranker: bool = Field(default=False)
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    default_k: int = Field(default=4, gt=0)

    # Agent Settings
    memory_window: int = Field(default=10, gt=0)
    max_iterations: int = Field(default=3, gt=0)

    # Server Settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, gt=0, lt=65536)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
