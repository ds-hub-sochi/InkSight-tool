# INKSight Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenRouter API key
- Pre-built vector store at `backend/vector_store/`

## Quick Deployment

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# At minimum, set OPENROUTER_API_KEY
```

### 2. Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Access Application

- **Frontend**: <http://localhost:8020>
- **Backend API**: <http://localhost:8010>
- **API Documentation**: <http://localhost:8010/docs>

**Default Login:**

- Username: `testuser`
- Password: `secret`

## Manual Deployment

### Build and Start Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manage Services

```bash
# Check status
docker-compose ps

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]
```

## Directory Structure

```txt
agentic_RAG/
├── backend/
│   ├── Dockerfile
│   ├── vector_store/          # Pre-built vector database (required)
│   ├── users.json            # User authentication (auto-created)
│   └── uploads/              # File uploads directory
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── public/ocr_data/      # OCR images and results
├── docker-compose.yml
├── .env.example
└── deploy.sh / deploy.bat
```

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY` - **Required** for LLM functionality
- `LANGCHAIN_API_KEY` - Optional for tracing
- `LANGCHAIN_PROJECT` - Optional project name
- `SECRET_KEY` - JWT token secret (auto-generated if not set)

### User Management

Edit `backend/users.json` to add/modify users:

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
