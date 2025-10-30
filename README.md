# TechXConf Quiz Application

A complete, production-ready quiz platform with a FastAPI backend and modern React frontend. Perfect for technical assessments, educational quizzes, and competitive programming challenges.

## 🚀 Full-Stack Architecture

- **Frontend**: Modern React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + PostgreSQL + Redis + Python 3.11
- **Features**: Authentication, real-time quizzes, leaderboards, Excel import
- **Deployment**: Docker containerization with monitoring stack

## Features

### Backend Features
- 🔐 **JWT Authentication** with refresh tokens and role-based access control
- 📊 **Excel Import** for questions and answers with validation and error reporting
- 🚀 **Fast REST API** with async/await and automatic OpenAPI documentation
- 📈 **Real-time Leaderboards** with topic and global rankings
- 🔄 **Quiz Sessions** with randomization, time tracking, and detailed results
- 📦 **Docker Support** for easy deployment and development
- 🔍 **Monitoring** with Prometheus metrics, structured logging, and Sentry integration
- ⚡ **Redis Caching** for high-performance data access
- 🧪 **Comprehensive Testing** with pytest and testcontainers

### Frontend Features
- ⚡ **Modern React 18** with TypeScript for type safety
- 🎨 **Tailwind CSS** for responsive, mobile-first design
- 🔐 **Secure Authentication** with automatic token refresh
- 📱 **Interactive Quiz Interface** with real-time progress and timer
- 📊 **Detailed Results** with question-by-question breakdown
- 🏆 **Leaderboards** with filtering by topic and performance metrics
- 🎯 **User Profile** management and quiz history
- 🌐 **Progressive Web App** capabilities for mobile devices

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ and npm (for frontend development)

### Running Locally with Docker

The easiest way to run the application locally is using Docker Compose with the local configuration file.

#### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd techxconf_quiz_app
```

#### 2. Start All Services

```bash
# Start all services (Backend, PostgreSQL, Redis, Frontend)
docker compose -f docker-compose.local.yml up -d

# View logs
docker compose -f docker-compose.local.yml logs -f

# View specific service logs
docker compose -f docker-compose.local.yml logs -f backend
docker compose -f docker-compose.local.yml logs -f frontend
```

#### 3. Initialize Database

```bash
# Run database migrations
docker compose -f docker-compose.local.yml exec backend alembic upgrade head

# Create admin user (if needed for admin access)
docker compose -f docker-compose.local.yml exec backend python -c "
from app.core.database import get_db
from app.models.user import User
from app.utils.security import get_password_hash
import asyncio

async def create_admin():
    async for db in get_db():
        admin = User(
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            display_name='Admin',
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print('Admin user created!')
        break

asyncio.run(create_admin())
"
```

#### 4. Access the Application

The application will be available at:
- **Frontend (Quiz App)**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### 5. Stop Services

```bash
# Stop all services
docker compose -f docker-compose.local.yml down

# Stop and remove volumes (clears database)
docker compose -f docker-compose.local.yml down -v
```

### Import Sample Questions

To add quiz questions from an Excel file:

```bash
# Copy your Excel file to the project directory
# Then import it using the backend container
docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py your_questions.xlsx
```

### 1. Clone and Setup (Production Deployment)

```bash
# Clone the repository
git clone <your-repo-url>
cd techxconf_quiz_app

# Copy environment configuration
cp .env.example .env

# Edit .env file with your settings (optional for development)
# The default values work for Docker Compose setup
```

### 2. Run with Docker Compose (Production)

```bash
# Start all services (API, PostgreSQL, Redis, Monitoring)
docker-compose up -d

# View logs
docker-compose logs -f web

# Check service status
docker-compose ps
```

The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173 (during development)
- **Health Check**: http://localhost:8000/health
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Flower (Celery)**: http://localhost:5555

### 3. Setup Frontend (Development)

```bash
# Install frontend dependencies
cd frontend
npm install

# Start frontend development server
npm run dev
```

The React frontend will be available at http://localhost:5173 with automatic hot reloading.

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec web python scripts/manage.py upgrade

# Create admin user
docker-compose exec web python scripts/manage.py create-admin \
  --email admin@example.com \
  --password AdminPassword123!

# Import sample questions (after creating questions.xlsx)
docker-compose exec web python scripts/import_xlsx.py Cloud_AI_Quiz_100.xlsx
```

## Local Development Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Database Services

```bash
# Start only PostgreSQL and Redis
docker-compose up -d db redis

# Or use local installations
# PostgreSQL: createdb quiz_db
# Redis: redis-server
```

### 3. Setup Database

```bash
# Set environment variables
export DATABASE_URL="postgresql+asyncpg://quiz_user:quiz_password@localhost:5432/quiz_db"
export REDIS_URL="redis://localhost:6379/0"

# Run migrations
python scripts/manage.py upgrade

# Create admin user
python scripts/manage.py create-admin
```

### 4. Run Development Server

```bash
# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Authentication

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "UserPassword123!",
    "display_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "UserPassword123!"
  }'

# Use the returned access_token in subsequent requests
export TOKEN="your_access_token_here"
```

### Quiz Operations

```bash
# Get available quizzes
curl "http://localhost:8000/api/v1/quizzes/"

# Get quiz details
curl "http://localhost:8000/api/v1/quizzes/ai_quiz"

# Start a quiz session
curl -X POST "http://localhost:8000/api/v1/quizzes/ai_quiz/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "num_questions": 10,
    "difficulty_mix": {"easy": 6, "medium": 3, "hard": 1}
  }'

# Get a question (use session_id from start response)
curl "http://localhost:8000/api/v1/quizzes/sessions/{session_id}/question/0" \
  -H "Authorization: Bearer $TOKEN"

# Submit an answer
curl -X POST "http://localhost:8000/api/v1/quizzes/sessions/{session_id}/answer" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "question_uuid",
    "selected_option": "B",
    "time_taken_ms": 5000
  }'

# Finish session and get results
curl -X POST "http://localhost:8000/api/v1/quizzes/sessions/{session_id}/finish" \
  -H "Authorization: Bearer $TOKEN"

# Get leaderboard
curl "http://localhost:8000/api/v1/quizzes/leaderboard"
```

## Question Import

### Excel File Format

The system expects an Excel file with two sheets:

**Questions Sheet:**
| ID | Topic | Difficulty | Question | Option A | Option B | Option C | Option D |
|----|--------|------------|----------|----------|----------|----------|----------|
| 1  | AI     | Easy       | What is supervised learning? | Learning without labels | Learning with labeled data | Learning alone | Online learning |
| 2  | AI     | Medium     | What is the Turing Test?     | Programming test        | Test for machine intelligence | Database test | Security test |

**Answers Sheet:**
| ID | Correct Option | Correct Answer Text | Short Explanation |
|----|----------------|---------------------|-------------------|
| 1  | B              | Learning with labeled data | Supervised learning uses labeled data to train models. |
| 2  | B              | Test for machine intelligence | The Turing Test measures machine ability to exhibit human-like intelligence. |

### Import Methods

#### CLI Import
```bash
# Preview import (validation only)
python scripts/import_xlsx.py questions.xlsx --mode preview

# Import with upsert (update existing, create new)
python scripts/import_xlsx.py questions.xlsx --mode upsert

# Import with replace mode
python scripts/import_xlsx.py questions.xlsx --mode replace
```

#### API Import (Admin only)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/questions/import" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@questions.xlsx"
```

## Database Management

```bash
# Create migration
python scripts/manage.py revision -m "Add new feature"

# Run migrations
python scripts/manage.py upgrade

# Rollback migration
python scripts/manage.py downgrade

# Show migration history
python scripts/manage.py history

# Create/drop tables (development only)
python scripts/manage.py create-tables
python scripts/manage.py drop-tables
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run integration tests
pytest tests/integration/
```

## Deployment

### Docker Production Build

```bash
# Build production image
docker build -t quiz-api:latest .

# Run production container
docker run -d \
  --name quiz-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@db:5432/quiz_db" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e SECRET_KEY="your-production-secret-key" \
  quiz-api:latest
```

### AWS Deployment (ECS/Fargate)

1. **Build and push to ECR:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t quiz-api .
docker tag quiz-api:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/quiz-api:latest

# Push
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/quiz-api:latest
```

2. **Setup infrastructure:**
   - RDS PostgreSQL database
   - ElastiCache Redis cluster
   - ECS cluster with Fargate service
   - Application Load Balancer with HTTPS
   - Secrets Manager for environment variables

3. **Environment variables for production:**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@rds-endpoint:5432/quiz_db
REDIS_URL=redis://elasticache-endpoint:6379/0
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
SENTRY_DSN=https://your-sentry-dsn
```

### DigitalOcean App Platform

1. **Create app.yaml:**
```yaml
name: quiz-api
services:
- name: web
  source_dir: /
  github:
    repo: your-username/quiz-backend
    branch: main
  run_command: gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8080 app.main:app
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${quiz-db.DATABASE_URL}
  - key: REDIS_URL
    value: ${quiz-redis.REDIS_URL}
  http_port: 8080

databases:
- name: quiz-db
  engine: PG
  version: "13"

- name: quiz-redis
  engine: REDIS
  version: "6"
```

## Monitoring and Observability

### Metrics (Prometheus)
- Request latency and throughput
- Database connection pool usage
- Redis cache hit rates
- Active quiz sessions
- Error rates by endpoint

### Logging
- Structured JSON logs with request IDs
- User actions and quiz events
- Import operations and errors
- Authentication events

### Alerts
- High error rates (>5%)
- High response times (>2s)
- Database connection issues
- Memory/CPU usage spikes

## Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=development|production
DEBUG=true|false
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR

# Features
RATE_LIMIT_PER_MINUTE=100
SESSION_EXPIRE_HOURS=48
MAX_FILE_SIZE_MB=50

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
PROMETHEUS_METRICS_ENABLED=true
```

## API Documentation

Once the application is running, visit:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   ```bash
   # Check database is running
   docker-compose ps db

   # Check connection
   docker-compose exec db psql -U quiz_user -d quiz_db
   ```

2. **Redis connection errors:**
   ```bash
   # Check Redis is running
   docker-compose ps redis

   # Test connection
   docker-compose exec redis redis-cli ping
   ```

3. **Import validation errors:**
   ```bash
   # Use preview mode to see errors
   python scripts/import_xlsx.py file.xlsx --mode preview
   ```

4. **Permission errors:**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.py
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug mode
export DEBUG=true
python -m uvicorn app.main:app --reload --log-level debug
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs web`
3. Check health endpoint: `curl http://localhost:8000/health`
4. Open an issue in the project repository