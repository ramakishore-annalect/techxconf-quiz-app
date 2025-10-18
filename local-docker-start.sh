#!/bin/bash

# Local Docker Full-Stack Setup Script
# This script helps you run your full-stack app locally with Docker

set -e  # Exit on error

echo "🚀 TechXConf Quiz App - Local Docker Setup"
echo "==========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker Desktop first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo -e "${YELLOW}! .env file not found. Creating one...${NC}"
    cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=quiz_password_local_dev
POSTGRES_DB=quiz_db

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Application Settings
SECRET_KEY=local-dev-secret-key-change-in-production
JWT_SECRET_KEY=local-dev-jwt-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
EOF
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo "What would you like to do?"
echo "1) Start all services (recommended)"
echo "2) Start backend only (PostgreSQL + Redis + FastAPI)"
echo "3) Start frontend only"
echo "4) Stop all services"
echo "5) Reset database (remove all data)"
echo "6) View logs"
echo "7) Run database migrations"
echo "8) Import quiz questions"
read -p "Choose option (1-8): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Starting all services...${NC}"
        docker-compose -f docker-compose.local.yml up --build
        ;;
    2)
        echo ""
        echo -e "${BLUE}Starting backend services...${NC}"
        docker-compose -f docker-compose.local.yml up --build postgres redis web
        ;;
    3)
        echo ""
        echo -e "${BLUE}Starting frontend only...${NC}"
        docker-compose -f docker-compose.local.yml up --build frontend
        ;;
    4)
        echo ""
        echo -e "${BLUE}Stopping all services...${NC}"
        docker-compose -f docker-compose.local.yml down
        echo -e "${GREEN}✓ All services stopped${NC}"
        ;;
    5)
        echo ""
        echo -e "${RED}⚠️  WARNING: This will delete all database data!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            docker-compose -f docker-compose.local.yml down -v
            echo -e "${GREEN}✓ Database reset complete${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    6)
        echo ""
        echo -e "${BLUE}Viewing logs (Ctrl+C to exit)...${NC}"
        docker-compose -f docker-compose.local.yml logs -f
        ;;
    7)
        echo ""
        echo -e "${BLUE}Running database migrations...${NC}"
        docker-compose -f docker-compose.local.yml exec web alembic upgrade head
        echo -e "${GREEN}✓ Migrations complete${NC}"
        ;;
    8)
        echo ""
        if [ ! -f "Cloud_AI_Quiz_450.xlsx" ]; then
            echo -e "${RED}✗ Cloud_AI_Quiz_450.xlsx not found in current directory${NC}"
            exit 1
        fi
        echo -e "${BLUE}Importing quiz questions...${NC}"
        docker-compose -f docker-compose.local.yml exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
        echo -e "${GREEN}✓ Questions imported${NC}"
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}Done!${NC}"
echo "=========================================="
echo ""
echo "Access your app:"
echo "  Frontend:    http://localhost:3000"
echo "  Backend API: http://localhost:8000/docs"
echo "  Health:      http://localhost:8000/health"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose -f docker-compose.local.yml logs -f"
echo "  Stop services:   docker-compose -f docker-compose.local.yml down"
echo "  Restart backend: docker-compose -f docker-compose.local.yml restart web"
echo "  Restart frontend: docker-compose -f docker-compose.local.yml restart frontend"
echo ""
echo -e "${BLUE}Happy coding! 🎉${NC}"
