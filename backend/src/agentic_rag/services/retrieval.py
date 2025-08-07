from typing import List, Optional, Tuple
from langchain.schema import Document

from .vector_store import VectorStoreManager
from .reranker import SemanticReranker


class RetrievalService:
    """Service for retrieving relevant documents from vector store."""

    def __init__(
        self,
        vector_store_path: str = "./vector_store",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        enable_reranker: bool = False,
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        """Initialize the retrieval service.

        Args:
            vector_store_path: Path to the vector store
            embedding_model: Embedding model to use
            enable_reranker: Whether to enable semantic reranking
            reranker_model: Cross-encoder model for reranking
        """
        self.vector_store = VectorStoreManager(
            persist_directory=vector_store_path, embedding_model=embedding_model
        )

        self.reranker = SemanticReranker(
            model_name=reranker_model, enabled=enable_reranker
        )

    def retrieve_documents(
        self,
        query: str,
        k: int = 4,
        use_reranker: bool = None,
        rerank_top_k: int = None,
        similarity_threshold: float = None,
        metadata_filter: Optional[dict] = None,
    ) -> List[Document]:
        """Retrieve relevant documents for a query.

        Args:
            query: Search query
            k: Number of documents to retrieve initially
            use_reranker: Whether to use reranker (overrides default)
            rerank_top_k: Number of documents to return after reranking
            similarity_threshold: Minimum similarity score threshold
            metadata_filter: Filter documents by metadata

        Returns:
            List of relevant documents
        """
        # Initialize vector store if needed
        if not self.vector_store.vector_store:
            self.vector_store.initialize_store()

        # Initial retrieval with higher k if reranking
        initial_k = k * 2 if (use_reranker or self.reranker.enabled) else k

        if similarity_threshold:
            # Get documents with scores for filtering
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=query, k=initial_k, filter_dict=metadata_filter
            )

            # Filter by similarity threshold
            filtered_docs = [
                doc for doc, score in docs_with_scores if score >= similarity_threshold
            ]
        else:
            # Simple similarity search
            filtered_docs = self.vector_store.similarity_search(
                query=query, k=initial_k, filter_dict=metadata_filter
            )

        # Apply reranking if enabled
        if use_reranker or (use_reranker is None and self.reranker.enabled):
            final_k = rerank_top_k or k
            filtered_docs = self.reranker.rerank_documents(
                query=query, documents=filtered_docs, top_k=final_k
            )
        else:
            # Return top k without reranking
            filtered_docs = filtered_docs[:k]

        return filtered_docs

    def retrieve_with_scores(
        self,
        query: str,
        k: int = 4,
        use_reranker: bool = None,
        rerank_top_k: int = None,
        metadata_filter: Optional[dict] = None,
    ) -> List[Tuple[Document, float]]:
        """Retrieve documents with similarity/relevance scores.

        Args:
            query: Search query
            k: Number of documents to retrieve initially
            use_reranker: Whether to use reranker
            rerank_top_k: Number of documents to return after reranking
            metadata_filter: Filter documents by metadata

        Returns:
            List of (document, score) tuples
        """
        if not self.vector_store.vector_store:
            self.vector_store.initialize_store()

        initial_k = k * 2 if (use_reranker or self.reranker.enabled) else k

        # Get initial results with scores
        docs_with_scores = self.vector_store.similarity_search_with_score(
            query=query, k=initial_k, filter_dict=metadata_filter
        )

        # Apply reranking if enabled
        if use_reranker or (use_reranker is None and self.reranker.enabled):
            final_k = rerank_top_k or k
            documents = [doc for doc, _ in docs_with_scores]
            return self.reranker.rerank_with_scores(
                query=query, documents=documents, top_k=final_k
            )

        return docs_with_scores[:k]

    def get_context_string(
        self,
        query: str,
        k: int = 4,
        separator: str = "\n\n---\n\n",
        include_metadata: bool = False,
        **kwargs,
    ) -> str:
        """Get retrieved documents as a single context string.

        Args:
            query: Search query
            k: Number of documents to retrieve
            separator: Separator between documents
            include_metadata: Whether to include document metadata
            **kwargs: Additional arguments for retrieve_documents

        Returns:
            Combined context string
        """
        documents = self.retrieve_documents(query=query, k=k, **kwargs)

        context_parts = []
        for i, doc in enumerate(documents):
            content = doc.page_content

            if include_metadata and doc.metadata:
                metadata_str = ", ".join(
                    [
                        f"{k}: {v}"
                        for k, v in doc.metadata.items()
                        if k not in ["source", "page"]  # Common metadata to exclude
                    ]
                )
                if metadata_str:
                    content = f"[{metadata_str}]\n{content}"

            context_parts.append(content)

        return separator.join(context_parts)

    def is_store_ready(self) -> bool:
        """Check if the vector store is ready for retrieval."""
        return self.vector_store._store_exists()

    def get_store_info(self) -> dict:
        """Get information about the vector store."""
        if not self.vector_store.vector_store:
            self.vector_store.initialize_store()

        return {
            "document_count": self.vector_store.get_collection_count(),
            "reranker_enabled": self.reranker.enabled,
            "reranker_model": (
                self.reranker.model_name if self.reranker.enabled else None
            ),
        }
