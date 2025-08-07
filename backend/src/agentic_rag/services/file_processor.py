import io
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from langchain.document_loaders import TextLoader
from langchain.document_loaders.pdf import PyPDF2Loader
from langchain.schema import Document


class FileProcessor:
    """Handles processing of uploaded files from bytes."""

    SUPPORTED_EXTENSIONS = {".txt", ".pdf"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

    def process_uploaded_file(
        self, file_bytes: bytes, filename: str, metadata: Optional[dict] = None
    ) -> Tuple[List[Document], dict]:
        """Process an uploaded file from bytes.

        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            metadata: Additional metadata

        Returns:
            Tuple of (documents, file_info)
        """
        # Validate file
        file_info = self._validate_file(file_bytes, filename)

        # Extract file extension
        file_path = Path(filename)
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        # Add metadata
        doc_metadata = metadata or {}
        doc_metadata.update(
            {
                "source": filename,
                "file_size": len(file_bytes),
                "file_type": extension[1:],  # Remove the dot
            }
        )

        # Process based on file type
        if extension == ".txt":
            documents = self._process_text_bytes(file_bytes, doc_metadata)
        elif extension == ".pdf":
            documents = self._process_pdf_bytes(file_bytes, doc_metadata)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

        return documents, file_info

    def _validate_file(self, file_bytes: bytes, filename: str) -> dict:
        """Validate uploaded file."""
        file_size = len(file_bytes)

        if file_size == 0:
            raise ValueError("File is empty")

        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds maximum allowed size ({self.MAX_FILE_SIZE} bytes)"
            )

        file_path = Path(filename)
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {extension}")

        return {
            "filename": filename,
            "size_bytes": file_size,
            "extension": extension,
            "size_mb": round(file_size / (1024 * 1024), 2),
        }

    def _process_text_bytes(self, file_bytes: bytes, metadata: dict) -> List[Document]:
        """Process text file from bytes."""
        try:
            # Try UTF-8 first
            text_content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                text_content = file_bytes.decode("latin-1")
            except UnicodeDecodeError:
                raise ValueError(
                    "Unable to decode text file. Please ensure it's in UTF-8 or Latin-1 encoding."
                )

        # Create document
        document = Document(page_content=text_content, metadata=metadata)

        return [document]

    def _process_pdf_bytes(self, file_bytes: bytes, metadata: dict) -> List[Document]:
        """Process PDF file from bytes."""
        # Create a temporary file to use with PyPDF2Loader
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            # Use PyPDF2Loader with temporary file
            loader = PyPDF2Loader(temp_file_path)
            documents = loader.load()

            # Update metadata for all pages
            for i, doc in enumerate(documents):
                doc.metadata.update(metadata)
                doc.metadata["page"] = i + 1

            return documents

        finally:
            # Clean up temporary file
            try:
                Path(temp_file_path).unlink()
            except Exception:
                pass  # Ignore cleanup errors

    @staticmethod
    def get_supported_extensions() -> List[str]:
        """Get list of supported file extensions."""
        return list(FileProcessor.SUPPORTED_EXTENSIONS)

    @staticmethod
    def is_supported_file(filename: str) -> bool:
        """Check if file extension is supported."""
        extension = Path(filename).suffix.lower()
        return extension in FileProcessor.SUPPORTED_EXTENSIONS
