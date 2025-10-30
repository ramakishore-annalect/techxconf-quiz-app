#!/bin/bash
###############################################################################
# TechXConf Quiz Application - Complete Setup Script
# Works on: macOS and Linux
# 
# This script sets up and runs the entire quiz application with all 
# dependencies, database migrations, and sample data loading.
#
# Usage:
#   ./setup.sh                    # Full setup with sample questions
#   ./setup.sh --skip-questions   # Setup without loading questions
#   ./setup.sh --reset            # Reset and rebuild everything
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Output functions
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_info() { echo -e "${CYAN}ℹ${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_step() { echo -e "\n${MAGENTA}==> $1${NC}"; }

# Parse arguments
SKIP_QUESTIONS=false
RESET=false
QUESTIONS_FILE="Cloud_AI_Quiz_450.xlsx"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-questions)
            SKIP_QUESTIONS=true
            shift
            ;;
        --reset)
            RESET=true
            shift
            ;;
        --questions-file)
            QUESTIONS_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-questions] [--reset] [--questions-file FILE]"
            exit 1
            ;;
    esac
done

# Banner
cat << "EOF"

╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   TechXConf Quiz Application Setup                       ║
║   Complete Automated Setup Script                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

EOF

# Step 1: Prerequisites Check
print_step "Checking Prerequisites"

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker is installed: $DOCKER_VERSION"
else
    print_error "Docker is not installed"
    print_info "Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

# Check Docker Compose
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    print_success "Docker Compose is available: $COMPOSE_VERSION"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Check if Docker daemon is running
if docker ps &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

# Step 2: Check/Create .env file
print_step "Setting up environment configuration"

if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# Step 3: Clean up old containers if reset requested
if [ "$RESET" = true ]; then
    print_step "Resetting application (removing old containers and volumes)"
    docker compose -f docker-compose.local.yml down -v 2>/dev/null || true
    print_success "Old containers and volumes removed"
fi

# Step 4: Stop running containers
print_step "Stopping any running containers"
docker compose -f docker-compose.local.yml down 2>/dev/null || true
print_success "Stopped existing containers"

# Step 5: Build and start services
print_step "Building and starting all services (this may take a few minutes)"
print_info "Building Docker images..."

if docker compose -f docker-compose.local.yml build --quiet; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

print_info "Starting services..."
if docker compose -f docker-compose.local.yml up -d; then
    print_success "Services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 6: Wait for services to be healthy
print_step "Waiting for services to be ready"

MAX_WAIT=60
WAITED=0
INTERVAL=2

print_info "Waiting for PostgreSQL to be healthy..."
while [ $WAITED -lt $MAX_WAIT ]; do
    if docker compose -f docker-compose.local.yml ps postgres --format json | grep -q '"Health":"healthy"'; then
        print_success "PostgreSQL is ready"
        break
    fi
    sleep $INTERVAL
    WAITED=$((WAITED + INTERVAL))
    echo -n "."
done
echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    print_error "PostgreSQL failed to become healthy"
    docker compose -f docker-compose.local.yml logs postgres
    exit 1
fi

print_info "Waiting for Redis to be healthy..."
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if docker compose -f docker-compose.local.yml ps redis --format json | grep -q '"Health":"healthy"'; then
        print_success "Redis is ready"
        break
    fi
    sleep $INTERVAL
    WAITED=$((WAITED + INTERVAL))
    echo -n "."
done
echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    print_error "Redis failed to become healthy"
    docker compose -f docker-compose.local.yml logs redis
    exit 1
fi

# Step 7: Wait for backend to start
print_info "Waiting for backend to be ready..."
sleep 5

if docker compose -f docker-compose.local.yml ps backend --format json | grep -q '"State":"running"'; then
    print_success "Backend is running"
else
    print_error "Backend is not running"
    docker compose -f docker-compose.local.yml logs backend
    exit 1
fi

# Step 8: Run database migrations
print_step "Running database migrations"
if docker compose -f docker-compose.local.yml exec -T backend alembic upgrade head; then
    print_success "Database migrations completed"
else
    print_error "Database migrations failed"
    docker compose -f docker-compose.local.yml logs backend
    exit 1
fi

# Step 9: Create admin user
print_step "Creating admin user"
docker compose -f docker-compose.local.yml exec -T backend python << 'PYTHON_SCRIPT'
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("Admin user already exists")
            return
        
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("Admin123!"),
            display_name="Admin User",
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: Admin123!")

asyncio.run(create_admin())
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    print_success "Admin user created (or already exists)"
    print_info "Admin credentials:"
    echo -e "   Email:    ${WHITE}admin@example.com${NC}"
    echo -e "   Password: ${WHITE}Admin123!${NC}"
else
    print_warning "Failed to create admin user (may already exist)"
fi

# Step 10: Import sample questions
if [ "$SKIP_QUESTIONS" = false ]; then
    print_step "Importing sample questions"
    
    if [ -f "$QUESTIONS_FILE" ]; then
        print_info "Importing questions from $QUESTIONS_FILE..."
        if docker compose -f docker-compose.local.yml exec -T backend python scripts/import_xlsx.py "$QUESTIONS_FILE" --mode upsert; then
            print_success "Sample questions imported successfully"
        else
            print_warning "Failed to import questions, but application will still work"
            print_info "You can manually import questions later using:"
            echo -e "   ${NC}docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py <file.xlsx>"
        fi
    else
        print_warning "Questions file '$QUESTIONS_FILE' not found"
        print_info "Available question files:"
        ls -1 *.xlsx 2>/dev/null | sed 's/^/   - /' || echo "   No .xlsx files found"
    fi
fi

# Step 11: Wait for frontend to be ready
print_step "Waiting for frontend to be ready"
sleep 5

if docker compose -f docker-compose.local.yml ps frontend --format json | grep -q '"State":"running"'; then
    print_success "Frontend is running"
else
    print_warning "Frontend is not running, checking logs..."
    docker compose -f docker-compose.local.yml logs frontend --tail 20
fi

# Step 12: Health check
print_step "Performing health checks"

if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed, but service may still be starting"
fi

# Step 13: Display status
print_step "Deployment Summary"

echo ""
echo -e "${CYAN}Services Status:${NC}"
docker compose -f docker-compose.local.yml ps --format "table {{.Service}}\t{{.State}}\t{{.Status}}"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║   🎉 Setup Complete! Application is ready to use! 🎉     ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Access your application at:${NC}"
echo -e "  • Frontend (Quiz App):  ${YELLOW}http://localhost:3000${NC}"
echo -e "  • Backend API:          ${YELLOW}http://localhost:8000${NC}"
echo -e "  • API Documentation:    ${YELLOW}http://localhost:8000/docs${NC}"
echo ""

echo -e "${CYAN}Admin Login:${NC}"
echo -e "  • Email:    ${WHITE}admin@example.com${NC}"
echo -e "  • Password: ${WHITE}Admin123!${NC}"
echo ""

echo -e "${CYAN}Useful Commands:${NC}"
echo -e "  • View logs:           ${NC}docker compose -f docker-compose.local.yml logs -f"
echo -e "  • Stop application:    ${NC}docker compose -f docker-compose.local.yml down"
echo -e "  • Restart application: ${NC}docker compose -f docker-compose.local.yml restart"
echo -e "  • Import questions:    ${NC}docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py <file.xlsx>"
echo ""

print_success "Setup completed successfully!"
