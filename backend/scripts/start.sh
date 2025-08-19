#!/bin/bash

# 🚀 CarbonTrack Backend Startup Script

set -e

echo "🌱 Starting CarbonTrack Backend..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please update .env file with your configuration before running in production${NC}"
fi

# Ensure we're in the backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo -e "${BLUE}📍 Working directory: $(pwd)${NC}"

# Run the server
echo -e "${GREEN}🚀 Starting FastAPI server...${NC}"
echo -e "${BLUE}📚 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${BLUE}🔄 ReDoc Documentation: http://localhost:8000/redoc${NC}"
echo -e "${BLUE}🏥 Health Check: http://localhost:8000/health${NC}"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
