#!/bin/bash

# Deployment Script

set -e

echo "Starting deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo " .env file not found. Please create one from .env.example"
    echo "cp .env.example .env"
    echo "Then edit .env with your API keys"
    exit 1
fi

# Check if vector store exists
if [ ! -d "backend/vector_store" ]; then
    echo "Vector store not found at backend/vector_store"
    echo "Please ensure the vector store is built and located at backend/vector_store/"
    exit 1
fi

# Check if users.json exists
if [ ! -f "backend/users.json" ]; then
    echo "users.json not found. Creating default users file..."
    cat > backend/users.json << 'EOF'
{
  "users": [
    {
      "username": "testuser",
      "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
      "is_active": true
    }
  ]
}
EOF
    echo "Created default users.json with testuser/secret"
fi

echo "Building Docker images..."
docker-compose build --no-cache

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo "Checking service health..."
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "Services are running and healthy!"
else
    echo "Services may still be starting. Check status with: docker-compose ps"
fi

echo ""
echo "Deployment complete!"
echo ""
echo "Access the application:"
echo "   Frontend: http://localhost:8020"
echo "   Backend API: http://localhost:8010"
echo "   API Docs: http://localhost:8010/docs"
echo ""
echo "Default login:"
echo "   Username: testuser"
echo "   Password: secret"
echo ""
echo "Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Status: docker-compose ps"