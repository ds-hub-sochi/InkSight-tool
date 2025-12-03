# 🚀 INKSight - AI-Powered RAG Assistant

<div align="center">

**Intelligent document processing system based on Retrieval-Augmented Generation**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178c6.svg)](https://www.typescriptlang.org/)

</div>

---

## 📋 About

**INKSight** is a modern document processing system that combines vector search capabilities with large language models. The system allows you to upload documents, index their content, and get accurate answers to questions with source citations.

### ✨ Key Features

- 🔍 **Vector Search** — fast semantic search across documents
- 💬 **Intelligent Chat** — interact with an AI assistant based on your documents
- 📄 **Document Processing** — support for PDF and text files
- 🔄 **Reranking** — improved relevance of search results
- 🔐 **Authentication** — secure access to the system
- 🐳 **Docker Deployment** — easy deployment via Docker Compose
- 📊 **Monitoring** — integration with LangSmith for request tracking

---

## 🏗️ Architecture

```
rag_chat/
├── backend/              # Python FastAPI backend
│   ├── src/
│   │   └── agentic_rag/
│   │       ├── api/      # API endpoints and routes
│   │       ├── core/     # Configuration and utilities
│   │       ├── models/   # LLM models
│   │       └── services/ # Business logic
│   ├── main.py          # FastAPI entry point
│   ├── cli.py           # CLI tools
│   └── vector_store/    # Vector database
│
├── frontend/            # React TypeScript frontend
│   ├── src/            # React components
│   └── dist/           # Built static assets
│
├── data/               # Source documents for indexing
├── docker-compose.yml  # Docker configuration
└── deploy.sh          # Deployment script
```

### System Components

- **Backend (FastAPI)** — REST API for request processing, vector store operations, and LLM integration
- **Frontend (React)** — modern web interface for system interaction
- **Vector Store (ChromaDB)** — vector database for storing document embeddings
- **LLM Integration** — integration with OpenRouter and local models
- **Document Processor** — document processing and chunking

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — modern Python web framework
- **LangChain** — framework for working with LLMs
- **ChromaDB** — vector database
- **Sentence Transformers** — models for creating embeddings
- **UV** — fast Python package manager
- **Pydantic** — data validation

### Frontend
- **React 18** — library for building user interfaces
- **TypeScript** — typed JavaScript
- **Vite** — fast build tool and dev server
- **Tailwind CSS** — utility-first CSS framework
- **TanStack Query** — server state management
- **Axios** — HTTP client

---

## 📦 Installation & Setup

### Requirements

- Python 3.12+
- Node.js 18+ and npm
- Docker and Docker Compose (for deployment)
- OpenRouter API key (or local model configuration)

### Local Development

#### 1. Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Copy environment template
cp .env.example .env
```

Configure the `.env` file:

```env
# Required parameters
OPENROUTER_API_KEY=your_openrouter_api_key_here
AGENT_LLM_MODEL=your_model_name
AGENT_API_KEY=your_api_key
AGENT_BASE_URL=your_base_url

# Optional parameters
LANGCHAIN_API_KEY=your_langsmith_api_key  # For tracing
LANGCHAIN_PROJECT=inksight                # Project name in LangSmith
SECRET_KEY=your-secret-key                # For JWT tokens
```

#### 2. Prepare Vector Database

```bash
cd backend

# Process documents from data folder
uv run python cli.py process ../data --clear

# Check vector store status
uv run python cli.py info
```

#### 3. Run Backend

```bash
cd backend
uv run python main.py --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

#### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build project
npm run build

# Run dev server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 🚀 Docker Deployment

### Quick Start

```bash
# Copy and configure .env
cp .env.example .env
# Edit .env file with your API keys

# Run deployment
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Service Management

```bash
# Check status
docker-compose ps

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

After deployment:
- **Frontend**: `http://localhost:8020`
- **Backend API**: `http://localhost:8010`
- **API Docs**: `http://localhost:8010/docs`

### Default Credentials

- **Username**: `testuser`
- **Password**: `secret`

> ⚠️ **Important**: Change the default password in production!

---

## 📡 API Endpoints

### Authentication

- `POST /api/v1/auth/login` — login to the system
- `GET /api/v1/auth/me` — current user information

### Main Endpoints

- `POST /api/v1/chat` — chat with AI assistant
- `POST /api/v1/search` — search knowledge base
- `POST /api/v1/upload` — upload documents
- `POST /api/v1/process-documents` — process documents
- `GET /api/v1/store-info` — vector store information
- `GET /api/v1/supported-formats` — supported file formats
- `POST /api/v1/clear-memory` — clear chat history
- `GET /api/v1/health` — system health check

Full API documentation available at: `http://localhost:8000/docs`

### API Usage Example

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "secret"}'

# Send message (requires auth token)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "What is machine learning?", "include_sources": true}'
```

---

## 💻 CLI Usage

The backend provides CLI tools for system management:

```bash
cd backend

# Process documents
uv run python cli.py process <path_to_documents> [--clear]

# Vector store information
uv run python cli.py info

# Clear vector store
uv run python cli.py clear
```

### Examples

```bash
# Process documents from data folder
uv run python cli.py process ../data

# Process with clearing existing database
uv run python cli.py process ../data --clear

# Check status
uv run python cli.py info
```

---

## ⚙️ Configuration

### Environment Variables

#### Required

- `OPENROUTER_API_KEY` — OpenRouter API key
- `AGENT_LLM_MODEL` — LLM model name
- `AGENT_API_KEY` — API key for model access
- `AGENT_BASE_URL` — base URL for model API

#### Optional

- `LANGCHAIN_API_KEY` — key for LangSmith (tracing)
- `LANGCHAIN_PROJECT` — project name in LangSmith
- `SECRET_KEY` — secret key for JWT tokens
- `USE_LOCAL_MODEL` — use local model
- `HOST` — server host (default: `0.0.0.0`)
- `PORT` — server port (default: `8000`)

### Document Processing Parameters

Settings can be changed in `backend/src/agentic_rag/core/config.py`:

- `chunk_size` — chunk size (default: 1000)
- `chunk_overlap` — overlap between chunks (default: 200)
- `embedding_model` — embedding model
- `default_k` — number of search results (default: 4)
- `enable_reranker` — enable reranking (default: `False`)

### User Management

Users are stored in `backend/users.json`. To add a new user:

```json
{
  "users": [
    {
      "username": "admin",
      "hashed_password": "bcrypt_hashed_password",
      "is_active": true
    }
  ]
}
```

> 💡 Use CLI or API for secure user creation with password hashing.

---

## 📚 Supported Formats

- **PDF** — PDF documents
- **TXT** — text files

Maximum file size: 10MB

---

## 🔧 Development

### Project Structure

```
backend/src/agentic_rag/
├── api/              # API endpoints
│   ├── routes.py     # Main routes
│   ├── auth_routes.py # Authentication routes
│   └── models.py     # Pydantic models
├── core/             # System core
│   ├── config.py     # Configuration
│   ├── auth.py       # Authentication
│   └── tracing.py    # Tracing
├── models/           # LLM models
│   └── llm.py        # LLM integration
└── services/         # Services
    ├── agent.py      # AI agent
    ├── retrieval.py  # Search
    ├── reranker.py   # Reranking
    ├── vector_store.py # Vector store
    ├── text_splitter.py # Text splitting
    ├── file_processor.py # File processing
    ├── document_loader.py # Document loading
    └── prompts.py    # Prompts
```

### Development Mode

```bash
# Backend with auto-reload
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend in dev mode
cd frontend
npm run dev
```

---

## 🐛 Troubleshooting

### Vector Store Issues

If the system cannot find documents:

```bash
cd backend
uv run python cli.py process ../data --clear
```

### API Key Issues

Make sure all required environment variables are set in the `.env` file:

```bash
# Check environment variables
cd backend
cat .env
```

### Docker Issues

```bash
# Rebuild images
docker-compose build --no-cache

# Clean and restart
docker-compose down -v
docker-compose up -d
```

### Dependency Issues

```bash
# Backend
cd backend
uv sync --upgrade

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 License

MIT License

---

## 👥 Authors

- **Aleksandr Tulenkov** — [@AleksandrTulenkov](https://github.com/AleksandrTulenkov)
- **Ivan Ulitin** — [@QQQiwi](https://github.com/QQQiwi)
- **Alexey Rastorguev** — [@Rastorguev763](https://github.com/Rastorguev763)
- **Maxim Novopoltsev** — [@maximazzik](https://github.com/maximazzik)
- **Ruslan Murtazin** — [@soltkreig](https://github.com/soltkreig)

---

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) — for the excellent LLM framework
- [FastAPI](https://fastapi.tiangolo.com/) — for the fast and modern web framework
- [ChromaDB](https://www.trychroma.com/) — for the vector database
- [OpenRouter](https://openrouter.ai/) — for access to various LLM models

---

<div align="center">

**Made with ❤️ for efficient document processing**

</div>
