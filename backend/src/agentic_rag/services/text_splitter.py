from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class TextChunker:
    """Handles text chunking for document processing."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
    ):
        """Initialize the text chunker.

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            separators: Custom separators for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if separators is None:
            separators = ["\n\n", "\n", " ", ""]

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        return self.text_splitter.split_documents(documents)

    def chunk_text(self, text: str, metadata: dict = None) -> List[Document]:
        """Split raw text into chunks."""
        if metadata is None:
            metadata = {}

        chunks = self.text_splitter.split_text(text)
        return [Document(page_content=chunk, metadata=metadata) for chunk in chunks]
