from typing import List, Optional, Tuple
from sentence_transformers import CrossEncoder
from langchain.schema import Document


class SemanticReranker:
    """Optional semantic reranker for improving search results quality."""

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        enabled: bool = False,
    ):
        """Initialize the semantic reranker.

        Args:
            model_name: Cross-encoder model for reranking
            enabled: Whether reranking is enabled
        """
        self.enabled = enabled
        self.model_name = model_name
        self.cross_encoder: Optional[CrossEncoder] = None

        if self.enabled:
            self._load_model()

    def _load_model(self) -> None:
        """Load the cross-encoder model."""
        try:
            self.cross_encoder = CrossEncoder(self.model_name)
        except Exception as e:
            print(f"Warning: Failed to load reranker model {self.model_name}: {e}")
            self.enabled = False

    def rerank_documents(
        self, query: str, documents: List[Document], top_k: Optional[int] = None
    ) -> List[Document]:
        """Rerank documents based on semantic similarity to query.

        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Number of top documents to return (None returns all)

        Returns:
            Reranked list of documents
        """
        if not self.enabled or not self.cross_encoder or not documents:
            return documents[:top_k] if top_k else documents

        try:
            # Prepare query-document pairs
            pairs = [(query, doc.page_content) for doc in documents]

            # Get relevance scores
            scores = self.cross_encoder.predict(pairs)

            # Combine documents with scores and sort
            doc_scores = list(zip(documents, scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)

            # Return top-k documents
            ranked_docs = [doc for doc, _ in doc_scores]
            return ranked_docs[:top_k] if top_k else ranked_docs

        except Exception as e:
            print(f"Warning: Reranking failed: {e}")
            return documents[:top_k] if top_k else documents

    def rerank_with_scores(
        self, query: str, documents: List[Document], top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """Rerank documents and return with relevance scores."""
        if not self.enabled or not self.cross_encoder or not documents:
            return [
                (doc, 0.0) for doc in documents[: top_k if top_k else len(documents)]
            ]

        try:
            pairs = [(query, doc.page_content) for doc in documents]
            scores = self.cross_encoder.predict(pairs)

            doc_scores = list(zip(documents, scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)

            return doc_scores[:top_k] if top_k else doc_scores

        except Exception as e:
            print(f"Warning: Reranking failed: {e}")
            return [
                (doc, 0.0) for doc in documents[: top_k if top_k else len(documents)]
            ]

    def enable_reranking(self) -> None:
        """Enable reranking functionality."""
        if not self.enabled:
            self.enabled = True
            self._load_model()

    def disable_reranking(self) -> None:
        """Disable reranking functionality."""
        self.enabled = False
        self.cross_encoder = None
