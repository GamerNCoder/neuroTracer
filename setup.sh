#!/bin/bash

# TraceNeuro Setup Script
# This script sets up the development environment for the TraceNeuro project

set -e

echo "🧠 Setting up TraceNeuro development environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python3 --version || { echo "Python 3.8+ required"; exit 1; }

# Check Node version
echo -e "${BLUE}Checking Node version...${NC}"
node --version || { echo "Node 16+ required"; exit 1; }

# Create virtual environment for Python
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies
echo -e "${BLUE}Installing Node dependencies...${NC}"
cd web && npm install && cd ..

# Create data directories
echo -e "${BLUE}Creating data directories...${NC}"
mkdir -p data/human data/ai data/hybrid
touch data/human/.gitkeep data/ai/.gitkeep data/hybrid/.gitkeep

# Create docs directory
mkdir -p docs

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start API server: cd api && uvicorn main:app --reload"
echo "  3. Start web dashboard: cd web && npm run dev"
echo ""

