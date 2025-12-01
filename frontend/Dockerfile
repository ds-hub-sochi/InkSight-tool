# Frontend Dockerfile for INKSight Agentic RAG System
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage — serve static files
FROM node:20-alpine

WORKDIR /app

# Install a lightweight static server
RUN npm install -g serve

# Copy build output
COPY --from=builder /app/dist ./dist

# Expose port (Traefik будет сюда проксировать)
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Run the static server
CMD ["serve", "-s", "dist", "-l", "3000"]
