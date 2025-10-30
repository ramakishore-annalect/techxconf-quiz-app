#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete setup script for TechXConf Quiz Application on Windows
.DESCRIPTION
    This script sets up and runs the entire quiz application with all dependencies,
    database migrations, and sample data loading.
.EXAMPLE
    .\setup.ps1
    Runs the complete setup
.EXAMPLE
    .\setup.ps1 -SkipQuestions
    Runs setup but skips loading sample questions
#>

param(
    [switch]$SkipQuestions,
    [switch]$Reset,
    [string]$QuestionsFile = "Cloud_AI_Quiz_450.xlsx"
)

# Color output functions
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[i] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[!] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[X] $Message" -ForegroundColor Red }
function Write-Step { param($Message) Write-Host "`n==> $Message" -ForegroundColor Magenta }

# Error handling
$ErrorActionPreference = "Stop"

# Banner
Write-Host @"

===============================================================
                                                              
   TechXConf Quiz Application Setup                       
   Complete Automated Setup Script                        
                                                              
===============================================================

"@ -ForegroundColor Cyan

# Step 1: Prerequisites Check
Write-Step "Checking Prerequisites"

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Success "Docker is installed: $dockerVersion"
}
catch {
    Write-Error "Docker is not installed or not in PATH"
    Write-Info "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker compose version
    Write-Success "Docker Compose is available: $composeVersion"
}
catch {
    Write-Error "Docker Compose is not available"
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Success "Docker daemon is running"
}
catch {
    Write-Error "Docker daemon is not running. Please start Docker Desktop."
    exit 1
}

# Step 2: Check/Create .env file
Write-Step "Setting up environment configuration"

if (-not (Test-Path ".env")) {
    Write-Info "Creating .env file from template..."
    Copy-Item ".env.example" ".env"
    Write-Success ".env file created"
}
else {
    Write-Success ".env file already exists"
}

# Step 3: Clean up old containers if reset requested
if ($Reset) {
    Write-Step "Resetting application (removing old containers and volumes)"
    docker compose -f docker-compose.local.yml down -v 2>$null
    Write-Success "Old containers and volumes removed"
}

# Step 4: Stop running containers
Write-Step "Stopping any running containers"
docker compose -f docker-compose.local.yml down 2>$null
Write-Success "Stopped existing containers"

# Step 5: Build and start services
Write-Step "Building and starting all services (this may take a few minutes)"
Write-Info "Building Docker images..."

docker compose -f docker-compose.local.yml build --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build Docker images"
    exit 1
}
Write-Success "Docker images built successfully"

Write-Info "Starting services..."
docker compose -f docker-compose.local.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start services"
    exit 1
}
Write-Success "Services started"

# Step 6: Wait for services to be healthy
Write-Step "Waiting for services to be ready"

$maxWait = 60
$waited = 0
$interval = 2

Write-Info "Waiting for PostgreSQL to be healthy..."
while ($waited -lt $maxWait) {
    $pgHealth = docker compose -f docker-compose.local.yml ps postgres --format json | ConvertFrom-Json | Select-Object -ExpandProperty Health
    if ($pgHealth -eq "healthy") {
        Write-Success "PostgreSQL is ready"
        break
    }
    Start-Sleep -Seconds $interval
    $waited += $interval
    Write-Host "." -NoNewline
}

if ($waited -ge $maxWait) {
    Write-Error "PostgreSQL failed to become healthy"
    docker compose -f docker-compose.local.yml logs postgres
    exit 1
}

Write-Info "Waiting for Redis to be healthy..."
$waited = 0
while ($waited -lt $maxWait) {
    $redisHealth = docker compose -f docker-compose.local.yml ps redis --format json | ConvertFrom-Json | Select-Object -ExpandProperty Health
    if ($redisHealth -eq "healthy") {
        Write-Success "Redis is ready"
        break
    }
    Start-Sleep -Seconds $interval
    $waited += $interval
    Write-Host "." -NoNewline
}

if ($waited -ge $maxWait) {
    Write-Error "Redis failed to become healthy"
    docker compose -f docker-compose.local.yml logs redis
    exit 1
}

# Step 7: Wait for backend to start
Write-Info "Waiting for backend to be ready..."
Start-Sleep -Seconds 5

$backendStatus = docker compose -f docker-compose.local.yml ps backend --format json | ConvertFrom-Json | Select-Object -ExpandProperty State
if ($backendStatus -ne "running") {
    Write-Error "Backend is not running"
    docker compose -f docker-compose.local.yml logs backend
    exit 1
}
Write-Success "Backend is running"

# Step 8: Run database migrations
Write-Step "Running database migrations"
docker compose -f docker-compose.local.yml exec -T backend alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Error "Database migrations failed"
    docker compose -f docker-compose.local.yml logs backend
    exit 1
}
Write-Success "Database migrations completed"

# Step 9: Create admin user
Write-Step "Creating admin user"
$createAdminScript = @'
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
'@

$createAdminScript | docker compose -f docker-compose.local.yml exec -T backend python

if ($LASTEXITCODE -eq 0) {
    Write-Success "Admin user created (or already exists)"
    Write-Info "Admin credentials:"
    Write-Host "   Email:    admin@example.com" -ForegroundColor White
    Write-Host "   Password: Admin123!" -ForegroundColor White
}
else {
    Write-Warning "Failed to create admin user (may already exist)"
}

# Step 10: Import sample questions
if (-not $SkipQuestions) {
    Write-Step "Importing sample questions"
    
    if (Test-Path $QuestionsFile) {
        Write-Info "Importing questions from $QuestionsFile..."
        docker compose -f docker-compose.local.yml exec -T backend python scripts/import_xlsx.py $QuestionsFile --mode upsert
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Sample questions imported successfully"
        }
        else {
            Write-Warning "Failed to import questions, but application will still work"
            Write-Info "You can manually import questions later using:"
            Write-Host "   docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py <file.xlsx>" -ForegroundColor Gray
        }
    }
    else {
        Write-Warning "Questions file '$QuestionsFile' not found"
        Write-Info "Available question files:"
        Get-ChildItem -Filter "*.xlsx" | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Gray }
    }
}

# Step 11: Wait for frontend to be ready
Write-Step "Waiting for frontend to be ready"
Start-Sleep -Seconds 5

$frontendStatus = docker compose -f docker-compose.local.yml ps frontend --format json | ConvertFrom-Json | Select-Object -ExpandProperty State
if ($frontendStatus -ne "running") {
    Write-Warning "Frontend is not running, checking logs..."
    docker compose -f docker-compose.local.yml logs frontend --tail 20
}
else {
    Write-Success "Frontend is running"
}

# Step 12: Health check
Write-Step "Performing health checks"

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Backend health check passed"
    }
}
catch {
    Write-Warning "Backend health check failed, but service may still be starting"
}

# Step 13: Display status
Write-Step "Deployment Summary"

Write-Host ""
$services = docker compose -f docker-compose.local.yml ps --format json | ConvertFrom-Json

Write-Host "Services Status:" -ForegroundColor Cyan
foreach ($service in $services) {
    $status = if ($service.State -eq "running") { "[OK]" } else { "[FAIL]" }
    $color = if ($service.State -eq "running") { "Green" } else { "Red" }
    Write-Host "  $status " -ForegroundColor $color -NoNewline
    Write-Host "$($service.Service): $($service.State)"
}

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Green
Write-Host "                                                              " -ForegroundColor Green
Write-Host "   SUCCESS! Application is ready to use!                     " -ForegroundColor Green
Write-Host "                                                              " -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Access your application at:" -ForegroundColor Cyan
Write-Host "  • Frontend (Quiz App):  " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Yellow
Write-Host "  • Backend API:          " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host "  • API Documentation:    " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

Write-Host "Admin Login:" -ForegroundColor Cyan
Write-Host "  • Email:    " -NoNewline; Write-Host "admin@example.com" -ForegroundColor White
Write-Host "  • Password: " -NoNewline; Write-Host "Admin123!" -ForegroundColor White
Write-Host ""

Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  • View logs:           " -NoNewline; Write-Host "docker compose -f docker-compose.local.yml logs -f" -ForegroundColor Gray
Write-Host "  • Stop application:    " -NoNewline; Write-Host "docker compose -f docker-compose.local.yml down" -ForegroundColor Gray
Write-Host "  • Restart application: " -NoNewline; Write-Host "docker compose -f docker-compose.local.yml restart" -ForegroundColor Gray
Write-Host "  • Import questions:    " -NoNewline; Write-Host "docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py <file.xlsx>" -ForegroundColor Gray
Write-Host ""

Write-Success "Setup completed successfully!"
