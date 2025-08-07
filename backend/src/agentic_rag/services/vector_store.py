from pathlib import Path
from typing import List, Optional
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


class VectorStoreManager:
    """Manages the local vector store for document embeddings."""

    def __init__(
        self,
        persist_directory: str = "./vector_store",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """Initialize the vector store manager.

        Args:
            persist_directory: Directory to persist the vector store
            embedding_model: HuggingFace embedding model to use
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model, model_kwargs={"device": "cpu"}
        )

        self.vector_store: Optional[Chroma] = None

    def initialize_store(self) -> None:
        """Initialize or load existing vector store."""
        if self._store_exists():
            self.vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
            )
        else:
            self.vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
            )

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        if not self.vector_store:
            self.initialize_store()

        if documents:
            self.vector_store.add_documents(documents)
            self.persist()

    def persist(self) -> None:
        """Persist the vector store to disk."""
        if self.vector_store:
            self.vector_store.persist()

    def similarity_search(
        self, query: str, k: int = 4, filter_dict: Optional[dict] = None
    ) -> List[Document]:
        """Search for similar documents."""
        if not self.vector_store:
            self.initialize_store()

        return self.vector_store.similarity_search(query=query, k=k, filter=filter_dict)

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter_dict: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """Search for similar documents with similarity scores."""
        if not self.vector_store:
            self.initialize_store()

        return self.vector_store.similarity_search_with_score(
            query=query, k=k, filter=filter_dict
        )

    def _store_exists(self) -> bool:
        """Check if vector store already exists."""
        return (self.persist_directory / "chroma.sqlite3").exists()

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        if not self.vector_store:
            self.initialize_store()

        return self.vector_store._collection.count()

    def clear_store(self) -> None:
        """Clear all documents from the vector store."""
        if self.vector_store:
            self.vector_store.delete_collection()
            self.vector_store = None

        # Remove persisted files
        if self.persist_directory.exists():
            import shutil

            shutil.rmtree(self.persist_directory)
            self.persist_directory.mkdir(parents=True, exist_ok=True)
