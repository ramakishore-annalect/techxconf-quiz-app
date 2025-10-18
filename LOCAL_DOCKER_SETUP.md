# Running Full-Stack App Locally with Docker

## 🎯 Quick Start (3 Commands)

```bash
# 1. Build and start all services
docker-compose up --build

# 2. Open your browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs

# 3. Stop services (Ctrl+C or)
docker-compose down
```

---

## 📋 Prerequisites

- Docker Desktop installed (includes docker-compose)
- Git repository cloned locally
- `.env` file configured (see below)

---

## 🔧 Setup Steps

### Step 1: Create `.env` File

Create a `.env` file in your project root:

```bash
# Copy the example
cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=quiz_password_local_dev
POSTGRES_DB=quiz_db
DB_HOST=postgres
DB_PORT=5432
DB_USER=quiz_user
DB_PASSWORD=quiz_password_local_dev
DB_NAME=quiz_db

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
```

### Step 2: Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

This will start:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis cache (port 6379)
- ✅ FastAPI backend (port 8000)
- ✅ React frontend (port 3000)

### Step 3: Run Database Migrations

**In a new terminal** (while services are running):

```bash
# Run migrations
docker-compose exec web alembic upgrade head

# Import quiz questions
docker-compose exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
```

### Step 4: Access Your App

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health

---

## 🐳 Docker Compose Commands

### Start Services
```bash
# Start all services (build if needed)
docker-compose up --build

# Start in background
docker-compose up -d

# Start specific service
docker-compose up postgres redis
```

### Stop Services
```bash
# Stop all services (Ctrl+C if in foreground)
docker-compose down

# Stop and remove volumes (deletes database data!)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Run Commands Inside Containers
```bash
# Run migrations
docker-compose exec web alembic upgrade head

# Import questions
docker-compose exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace

# Open Python shell
docker-compose exec web python

# Open database shell
docker-compose exec postgres psql -U quiz_user -d quiz_db

# Open bash in web container
docker-compose exec web bash
```

### Rebuild Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build web

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Check Service Status
```bash
# List running containers
docker-compose ps

# View resource usage
docker stats
```

---

## 🔍 Troubleshooting

### Port Already in Use

**Problem**: `Error: port 8000 already allocated`

**Solution**: Stop the conflicting service or change ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port to 8001
```

### Database Connection Error

**Problem**: `could not connect to server`

**Solution**: Make sure PostgreSQL is running:
```bash
docker-compose up postgres redis
# Wait 5 seconds for DB to start
docker-compose up web
```

### Frontend Can't Connect to Backend

**Problem**: API calls fail with CORS errors

**Solution**: Check `VITE_API_URL` in `.env`:
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Database Persists Old Data

**Problem**: Want to start fresh

**Solution**: Remove volumes and restart:
```bash
docker-compose down -v
docker-compose up --build
docker-compose exec web alembic upgrade head
```

### Docker Build Fails

**Problem**: Build errors or missing dependencies

**Solution**: Clear cache and rebuild:
```bash
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

---

## 📁 Project Structure

```
techxconf_quiz_app/
├── docker-compose.yml           # Orchestrates all services
├── Dockerfile                   # Backend container
├── frontend/
│   ├── Dockerfile              # Frontend container
│   ├── package.json
│   └── src/
├── app/                         # Backend code
├── alembic/                     # Database migrations
├── scripts/                     # Import scripts
└── .env                         # Local environment variables
```

---

## 🔐 Security Notes

### For Local Development:
- ✅ Use simple passwords (already in `.env` example)
- ✅ DEBUG=True is fine
- ✅ Expose all ports

### For Production:
- ❌ NEVER commit `.env` to git
- ❌ Change all secrets and passwords
- ❌ Set DEBUG=False
- ❌ Use strong, random keys

---

## 🎯 Common Workflows

### Start Fresh Database
```bash
docker-compose down -v
docker-compose up -d postgres redis
sleep 5  # Wait for DB to be ready
docker-compose up -d web
docker-compose exec web alembic upgrade head
docker-compose exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
docker-compose up -d frontend
```

### Update Frontend Code
```bash
# Frontend auto-reloads with Vite HMR
# Just edit files in frontend/src/
# Changes appear immediately in browser
```

### Update Backend Code
```bash
# If using docker-compose with volume mounts:
# Edit files in app/
# Container auto-reloads (if DEBUG=True)

# If not auto-reloading:
docker-compose restart web
```

### Run Tests
```bash
# Backend tests
docker-compose exec web pytest

# Frontend tests
docker-compose exec frontend npm test
```

### View Database
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U quiz_user -d quiz_db

# Run SQL
\dt                    # List tables
SELECT * FROM questions LIMIT 5;
\q                     # Quit
```

---

## 🚀 Performance Tips

### Speed Up Builds
1. Use `.dockerignore` to exclude unnecessary files
2. Leverage build cache (don't use `--no-cache` unless needed)
3. Multi-stage builds (already in Dockerfile)

### Reduce Memory Usage
```bash
# Limit resources in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Enable File Watching (Hot Reload)
Already configured in docker-compose.yml with volume mounts!

---

## 📚 Next Steps

1. ✅ Start services: `docker-compose up --build`
2. ✅ Run migrations: `docker-compose exec web alembic upgrade head`
3. ✅ Import questions: `docker-compose exec web python scripts/import_xlsx.py ...`
4. ✅ Open browser: http://localhost:3000
5. ✅ Start coding! Changes auto-reload.

---

## 🆘 Need Help?

- **Docker Docs**: https://docs.docker.com/compose/
- **View logs**: `docker-compose logs -f`
- **Restart service**: `docker-compose restart web`
- **Rebuild**: `docker-compose build --no-cache web`

---

**Your local development environment is ready! 🎉**
