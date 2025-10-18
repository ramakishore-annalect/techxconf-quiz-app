# 🚀 Local Docker Full-Stack - Quick Reference

## ⚡ Quick Start (Copy & Paste)

```bash
# 1. Start everything
docker-compose -f docker-compose.local.yml up --build

# 2. In a new terminal, run migrations
docker-compose -f docker-compose.local.yml exec web alembic upgrade head

# 3. Import questions (if you have the Excel file)
docker-compose -f docker-compose.local.yml exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace

# 4. Open browser
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/docs
```

---

## 🎯 Using the Interactive Script

```bash
./local-docker-start.sh
```

Choose option:
1. **Start all services** - Full-stack (frontend + backend + databases)
2. **Start backend only** - Just API and databases
3. **Start frontend only** - Just React app
4. **Stop all services** - Cleanup
5. **Reset database** - Delete all data and start fresh
6. **View logs** - Watch real-time logs
7. **Run migrations** - Update database schema
8. **Import questions** - Load quiz data

---

## 📦 What Gets Started

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Frontend | 3000 | http://localhost:3000 | React + TypeScript + Vite |
| Backend | 8000 | http://localhost:8000/docs | FastAPI + Swagger Docs |
| PostgreSQL | 5432 | localhost:5432 | Database |
| Redis | 6379 | localhost:6379 | Cache |

---

## 🔧 Common Commands

### Start/Stop
```bash
# Start all (foreground)
docker-compose -f docker-compose.local.yml up

# Start all (background)
docker-compose -f docker-compose.local.yml up -d

# Stop all
docker-compose -f docker-compose.local.yml down

# Stop and remove volumes (delete database)
docker-compose -f docker-compose.local.yml down -v
```

### Logs
```bash
# All services
docker-compose -f docker-compose.local.yml logs -f

# Specific service
docker-compose -f docker-compose.local.yml logs -f web
docker-compose -f docker-compose.local.yml logs -f frontend
docker-compose -f docker-compose.local.yml logs -f postgres
```

### Restart
```bash
# Restart backend
docker-compose -f docker-compose.local.yml restart web

# Restart frontend
docker-compose -f docker-compose.local.yml restart frontend

# Restart all
docker-compose -f docker-compose.local.yml restart
```

### Execute Commands
```bash
# Run migrations
docker-compose -f docker-compose.local.yml exec web alembic upgrade head

# Import questions
docker-compose -f docker-compose.local.yml exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace

# Python shell
docker-compose -f docker-compose.local.yml exec web python

# Database shell
docker-compose -f docker-compose.local.yml exec postgres psql -U quiz_user -d quiz_db

# Backend bash
docker-compose -f docker-compose.local.yml exec web bash

# Frontend bash
docker-compose -f docker-compose.local.yml exec frontend sh
```

### Build
```bash
# Rebuild all services
docker-compose -f docker-compose.local.yml build

# Rebuild backend only
docker-compose -f docker-compose.local.yml build web

# Force rebuild (no cache)
docker-compose -f docker-compose.local.yml build --no-cache
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.local.yml
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.local.yml ps

# View database logs
docker-compose -f docker-compose.local.yml logs postgres

# Restart database
docker-compose -f docker-compose.local.yml restart postgres
```

### Frontend Build Error
```bash
# Clear node_modules and rebuild
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml build --no-cache frontend
docker-compose -f docker-compose.local.yml up frontend
```

### "No such file or directory" Error
```bash
# Make sure you're in the project root
cd /Users/ramakishore.nooji/Annalect\ Code/techxconf_quiz_app

# Check if docker-compose.local.yml exists
ls -la docker-compose.local.yml
```

### Backend Not Auto-Reloading
```bash
# Check if volume mounts are correct in docker-compose.local.yml
# Make sure DEBUG=True in .env
# Restart backend:
docker-compose -f docker-compose.local.yml restart web
```

---

## 📁 Files Created for Local Development

- ✅ `docker-compose.local.yml` - Full-stack orchestration
- ✅ `frontend/Dockerfile.dev` - Frontend dev container
- ✅ `Dockerfile.dev` - Backend dev container (if not exists)
- ✅ `local-docker-start.sh` - Interactive startup script
- ✅ `.env` - Environment variables (auto-created)

---

## 🔐 Environment Variables

Created automatically in `.env`:

```bash
# Database
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=quiz_password_local_dev
POSTGRES_DB=quiz_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# App
SECRET_KEY=local-dev-secret-key
JWT_SECRET_KEY=local-dev-jwt-key
ENVIRONMENT=development
DEBUG=True

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🎯 Development Workflow

### 1. Start Services
```bash
./local-docker-start.sh
# Choose option 1
```

### 2. Run Migrations (First Time)
```bash
docker-compose -f docker-compose.local.yml exec web alembic upgrade head
```

### 3. Import Questions (First Time)
```bash
docker-compose -f docker-compose.local.yml exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
```

### 4. Code!
- Edit frontend code in `frontend/src/` - **Auto-reloads!** ⚡
- Edit backend code in `app/` - **Auto-reloads!** ⚡
- Changes appear immediately in browser

### 5. Test
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Try registering, logging in, taking a quiz

### 6. Stop Services
```bash
# Press Ctrl+C in terminal
# Or:
docker-compose -f docker-compose.local.yml down
```

---

## 📊 Resource Usage

Typical memory usage:
- PostgreSQL: ~50MB
- Redis: ~10MB
- Backend: ~200MB
- Frontend: ~100MB
- **Total: ~360MB**

---

## 🎉 You're Ready!

```bash
# Start coding
./local-docker-start.sh

# Choose option 1 (Start all services)
# Wait for services to start (~30 seconds)
# Open http://localhost:3000
# Happy coding! 🚀
```

---

## 📚 Full Documentation

See `LOCAL_DOCKER_SETUP.md` for comprehensive guide.
