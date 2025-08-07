import os
from pathlib import Path
from typing import List, Optional
from langchain.schema import Document

from .document_loader import DocumentLoader
from .text_splitter import TextChunker
from .vector_store import VectorStoreManager


class DataPreparationPipeline:
    """Pipeline for preparing documents and storing them in vector database."""

    def __init__(
        self,
        vector_store_path: str = "./vector_store",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """Initialize the data preparation pipeline.

        Args:
            vector_store_path: Path to store the vector database
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_model: Embedding model to use
        """
        self.document_loader = DocumentLoader()
        self.text_chunker = TextChunker(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self.vector_store = VectorStoreManager(
            persist_directory=vector_store_path, embedding_model=embedding_model
        )

    def process_documents(
        self, documents_path: str, clear_existing: bool = False
    ) -> int:
        """Process all documents in a directory and add to vector store.

        Args:
            documents_path: Path to directory containing documents
            clear_existing: Whether to clear existing vector store

        Returns:
            Number of document chunks processed
        """
        if clear_existing:
            print("Clearing existing vector store...")
            self.vector_store.clear_store()

        # Initialize vector store
        self.vector_store.initialize_store()

        # Load documents
        print(f"Loading documents from {documents_path}...")
        documents = self.document_loader.load_documents(documents_path)

        if not documents:
            print("No documents found to process.")
            return 0

        print(f"Loaded {len(documents)} documents.")

        # Chunk documents
        print("Chunking documents...")
        chunks = self.text_chunker.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks.")

        # Add to vector store
        print("Adding chunks to vector store...")
        self.vector_store.add_documents(chunks)

        print("Data preparation completed successfully.")
        return len(chunks)

    def process_single_document(
        self, file_path: str, metadata: Optional[dict] = None
    ) -> int:
        """Process a single document and add to vector store.

        Args:
            file_path: Path to the document file
            metadata: Additional metadata for the document

        Returns:
            Number of chunks created
        """
        # Load document
        documents = self.document_loader.load_document(file_path)

        if not documents:
            return 0

        # Add metadata if provided
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)

        # Chunk document
        chunks = self.text_chunker.chunk_documents(documents)

        # Initialize vector store if needed
        if not self.vector_store.vector_store:
            self.vector_store.initialize_store()

        # Add to vector store
        self.vector_store.add_documents(chunks)

        return len(chunks)

    def add_text_chunks(self, text: str, metadata: Optional[dict] = None) -> int:
        """Add raw text chunks to vector store.

        Args:
            text: Raw text to chunk and add
            metadata: Metadata for the text chunks

        Returns:
            Number of chunks created
        """
        chunks = self.text_chunker.chunk_text(text, metadata or {})

        if not self.vector_store.vector_store:
            self.vector_store.initialize_store()

        self.vector_store.add_documents(chunks)
        return len(chunks)

    def get_store_stats(self) -> dict:
        """Get statistics about the vector store."""
        if not self.vector_store.vector_store:
            self.vector_store.initialize_store()

        return {
            "document_count": self.vector_store.get_collection_count(),
            "store_exists": self.vector_store._store_exists(),
            "persist_directory": str(self.vector_store.persist_directory),
        }
