# Backend Dockerfile for INKSight Agentic RAG System
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy pyproject.toml and uv.lock first for better layer caching
COPY pyproject.toml ./
COPY uv.lock* ./

# Install Python dependencies
RUN uv sync --frozen

# Copy source code
COPY . .

# Copy existing vector store
COPY vector_store/ ./vector_store/

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uv", "run", "python", "main.py", "--host", "0.0.0.0", "--port", "8000"]