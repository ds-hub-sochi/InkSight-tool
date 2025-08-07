from pathlib import Path
from typing import List, Union
from langchain.document_loaders import TextLoader
from langchain.document_loaders.pdf import PyPDF2Loader
from langchain.schema import Document


class DocumentLoader:
    """Handles loading of TXT and PDF documents."""

    def load_document(self, file_path: Union[str, Path]) -> List[Document]:
        """Load a single document (TXT or PDF)."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == ".txt":
            return self._load_txt(file_path)
        elif file_path.suffix.lower() == ".pdf":
            return self._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def load_documents(self, directory_path: Union[str, Path]) -> List[Document]:
        """Load all TXT and PDF documents from a directory."""
        directory_path = Path(directory_path)

        if not directory_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory_path}")

        documents = []
        supported_extensions = [".txt", ".pdf"]

        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    docs = self.load_document(file_path)
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

        return documents

    def _load_txt(self, file_path: Path) -> List[Document]:
        """Load a TXT file."""
        loader = TextLoader(str(file_path))
        return loader.load()

    def _load_pdf(self, file_path: Path) -> List[Document]:
        """Load a PDF file."""
        loader = PyPDF2Loader(str(file_path))
        return loader.load()
