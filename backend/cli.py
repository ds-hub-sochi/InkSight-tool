#!/usr/bin/env python3
"""CLI tool for data preparation and system management."""

import argparse
import os

from src.agentic_rag.core.config import settings
from src.agentic_rag.services.data_pipeline import DataPreparationPipeline


def process_documents(documents_path: str, clear_existing: bool = False):
    """Process documents and add them to vector store."""
    if not os.path.exists(documents_path):
        print(f"Error: Documents path does not exist: {documents_path}")
        return

    print(f"Processing documents from: {documents_path}")
    print(f"Clear existing store: {clear_existing}")

    # Initialize data pipeline
    pipeline = DataPreparationPipeline(
        vector_store_path=settings.vector_store_path,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        embedding_model=settings.embedding_model,
    )

    try:
        chunks_processed = pipeline.process_documents(
            documents_path=documents_path, clear_existing=clear_existing
        )

        print(f"Successfully processed {chunks_processed} document chunks")

        # Show store stats
        stats = pipeline.get_store_stats()
        print("Vector store stats:")
        print(f"   - Total documents: {stats['document_count']}")
        print(f"   - Store location: {stats['persist_directory']}")

    except Exception as e:
        print(f"Error processing documents: {e}")


def show_store_info():
    """Show vector store information."""
    pipeline = DataPreparationPipeline(vector_store_path=settings.vector_store_path)

    stats = pipeline.get_store_stats()

    print("Vector Store Information:")
    print(f"   - Document count: {stats['document_count']}")
    print(f"   - Store exists: {stats['store_exists']}")
    print(f"   - Store location: {stats['persist_directory']}")
    print(f"   - Embedding model: {settings.embedding_model}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Agentic RAG System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process documents command
    process_parser = subparsers.add_parser(
        "process", help="Process documents and add to vector store"
    )
    process_parser.add_argument(
        "documents_path", help="Path to directory containing documents"
    )
    process_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing vector store before processing",
    )

    args = parser.parse_args()

    if args.command == "process":
        process_documents(args.documents_path, args.clear)
    elif args.command == "info":
        show_store_info()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
