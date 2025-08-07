# Agentic RAG System

A modern full-stack agentic RAG (Retrieval-Augmented Generation) system with a React TypeScript frontend and Python FastAPI backend. Upload documents, chat with AI, and get intelligent responses based on your knowledge base.

## Architecture

```
agentic_RAG/
├── backend/           # Python FastAPI backend
│   ├── src/          # Python source code
│   ├── main.py       # FastAPI application
│   ├── cli.py        # CLI tools
│   └── documents/    # Document storage
└── frontend/         # React TypeScript frontend
    ├── src/          # React components
    └── dist/         # Built frontend assets
```

## Features

### Backend (Python + FastAPI)
- **Document Processing**: TXT and PDF file support with intelligent chunking
- **Vector Search**: ChromaDB with HuggingFace embeddings
- **Agentic Chat**: ReAct agent with tool use capabilities
- **File Upload API**: Direct file upload from frontend
- **Semantic Reranking**: Optional cross-encoder reranking
- **LangSmith Integration**: Optional observability and tracing

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive interface built with Tailwind CSS
- **Real-time Chat**: Interactive chat interface with source attribution
- **File Upload**: Drag & drop document upload with progress feedback
- **System Monitoring**: Real-time status and health monitoring
- **TypeScript**: Full type safety with comprehensive API client

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here  # Optional
LANGCHAIN_PROJECT=agentic-rag
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
```

### 3. Start Development

**Terminal 1 - Backend:**
```bash
cd backend
uv run python main.py
# Backend starts at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend starts at http://localhost:3000
```

## Usage

1. **Upload Documents**: Go to the Upload tab and drag & drop TXT or PDF files
2. **Chat with AI**: Switch to the Chat tab and ask questions about your documents
3. **Monitor System**: Check the Status tab for system health and knowledge base info

## API Endpoints

The backend provides a comprehensive REST API:

- `POST /api/v1/chat` - Chat with the AI agent
- `POST /api/v1/upload` - Upload documents
- `POST /api/v1/search` - Search the knowledge base
- `GET /api/v1/store-info` - Get vector store information
- `GET /api/v1/health` - System health check

Full API documentation available at: `http://localhost:8000/docs`

## Configuration

### Backend (.env)
```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=agentic-rag
ENABLE_RERANKER=false
MODEL_NAME=anthropic/claude-3.5-sonnet
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - Agent and document processing framework  
- **ChromaDB** - Vector database for embeddings
- **OpenRouter** - LLM API access
- **HuggingFace** - Embeddings and reranking models
- **UV** - Fast Python package management

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast development server and build tool
- **Tailwind CSS** - Utility-first styling
- **TanStack Query** - Data fetching and caching
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client with interceptors

## Development

### Backend Development
```bash
cd backend
uv run python main.py --reload  # Auto-reload on changes
uv run black .                  # Format code
uv run python cli.py info       # Check vector store status
```

### Frontend Development
```bash
cd frontend
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint checking
npm run type-check   # TypeScript checking
```

## Production Deployment

### Backend
```bash
cd backend
uv run python main.py --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
# Serve the dist/ folder with any static file server
```

## License

MIT License