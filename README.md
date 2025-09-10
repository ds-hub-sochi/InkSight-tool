# Agentic RAG System

## Architecture

```txt
agentic_RAG/
├── backend/           # Python FastAPI backend
│   ├── src/          # Python source code
│   ├── main.py       # FastAPI application
│   ├── cli.py        # CLI tools
└── frontend/         # React TypeScript frontend
    ├── src/          # React components
    └── dist/         # Built frontend assets
```

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
LANGCHAIN_PROJECT=agentic-rag  # Optional
```

## API Endpoints

The backend provides a comprehensive REST API:

- `POST /api/v1/chat` - Chat with the AI agent
- `POST /api/v1/upload` - Upload documents
- `POST /api/v1/search` - Search the knowledge base
- `GET /api/v1/store-info` - Get vector store information
- `GET /api/v1/health` - System health check

Full API documentation available at: `http://localhost:8010/docs`

## Stack

### Backend

- **FastAPI**
- **LangChain**
- **ChromaDB**
- **OpenRouter**
- **HuggingFace**
- **UV**

### Frontend

- **React 18**
- **TypeScript**
- **Vite**
- **Tailwind CSS**
- **TanStack Query**
- **Lucide React**
- **Axios**

## Development

### DB

```bash
cd backend
uv run python cli.py process ../data --clear  # Build vector database from data folder
uv run python cli.py info       # Check vector store status
```

### Backend run

```bash
cd backend
uv run python main.py --host 0.0.0.0 --port 8000
```

### Frontend run

```bash
cd frontend
npm run build
npm run dev
```

###

test user credentials:
testuser
secret

## License

MIT License
