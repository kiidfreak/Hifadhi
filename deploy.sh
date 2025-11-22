#!/bin/bash

# Hifadhi Deployment Script - Production Ready

set -e  # Exit on error

echo "🚀 Hifadhi Multi-Agent System Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Edit with your keys"
    exit 1
fi

echo -e "${GREEN}✅ Environment file found${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data logs config

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build Docker image
echo ""
echo "📦 Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Start services
echo ""
echo "🏃 Starting Hifadhi services..."
echo ""
echo "Services:"
echo "  - Hifadhi API: http://localhost:8000"
echo "  - Phoenix Observability: http://localhost:6006"
echo ""

docker-compose up -d

# Check if services started
sleep 5

if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo "🌐 Access points:"
    echo "  - API:          http://localhost:8000"
    echo "  - API Docs:     http://localhost:8000/docs"
    echo "  - Phoenix UI:   http://localhost:6006"
    echo ""
    echo "📜 View logs:"
    echo "  docker-compose logs -f hifadhi"
    echo ""
    echo "🛑 Stop services:"
    echo "  docker-compose down"
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo "Check logs:"
    echo "  docker-compose logs"
    exit 1
fi
