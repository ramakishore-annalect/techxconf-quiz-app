# Quick Start Guide - TechXConf Quiz Application

This guide will help you set up and run the complete quiz application in just a few minutes using automated setup scripts.

## 🚀 One-Command Setup

### For Windows (PowerShell)

```powershell
# Run the setup script
.\setup.ps1
```

### For macOS/Linux (Bash)

```bash
# Make the script executable (first time only)
chmod +x setup.sh

# Run the setup script
./setup.sh
```

That's it! The script will:

- ✅ Check all prerequisites (Docker, Docker Compose)
- ✅ Create environment configuration
- ✅ Build and start all services (Backend, Frontend, PostgreSQL, Redis)
- ✅ Run database migrations
- ✅ Create an admin user
- ✅ Import sample quiz questions
- ✅ Verify everything is working

## 📋 Prerequisites

Before running the setup script, ensure you have:

1. **Docker Desktop** installed and running

   - Windows/Mac: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **Minimum System Requirements**
   - 4GB RAM available for Docker
   - 5GB free disk space
   - Ports available: 3000, 5432, 6379, 8000

## 🎯 Setup Options

### Basic Setup

```powershell
# Windows
.\setup.ps1

# Mac/Linux
./setup.sh
```

### Setup Without Sample Questions

```powershell
# Windows
.\setup.ps1 -SkipQuestions

# Mac/Linux
./setup.sh --skip-questions
```

### Complete Reset and Rebuild

```powershell
# Windows
.\setup.ps1 -Reset

# Mac/Linux
./setup.sh --reset
```

### Use Different Questions File

```powershell
# Windows
.\setup.ps1 -QuestionsFile "Cloud_AI_Quiz_400.xlsx"

# Mac/Linux
./setup.sh --questions-file "Cloud_AI_Quiz_400.xlsx"
```

## 🌐 Accessing the Application

After setup completes, access the application at:

| Service         | URL                        | Description                     |
| --------------- | -------------------------- | ------------------------------- |
| **Frontend**    | http://localhost:3000      | Main quiz application interface |
| **Backend API** | http://localhost:8000      | REST API endpoints              |
| **API Docs**    | http://localhost:8000/docs | Interactive API documentation   |

## 🔐 Default Credentials

**Admin Account:**

- Email: `admin@example.com`
- Password: `Admin123!`

**Regular User:**
You can register a new account through the frontend interface at http://localhost:3000

## 📊 What Gets Set Up

The setup script configures the following services:

```
┌─────────────────────────────────────────────┐
│  Frontend (React + Vite)                    │
│  Port: 3000                                 │
│  - Modern React 18 with TypeScript          │
│  - Tailwind CSS styling                     │
│  - Interactive quiz interface               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Backend API (FastAPI)                      │
│  Port: 8000                                 │
│  - JWT Authentication                       │
│  - REST API endpoints                       │
│  - Real-time quiz sessions                  │
└─────────────────────────────────────────────┘
           ↓                ↓
┌──────────────────┐  ┌─────────────────────┐
│  PostgreSQL      │  │  Redis              │
│  Port: 5432      │  │  Port: 6379         │
│  - Quiz data     │  │  - Session cache    │
│  - User accounts │  │  - Leaderboards     │
└──────────────────┘  └─────────────────────┘
```

## 🛠️ Common Commands

### View Application Logs

```bash
# All services
docker compose -f docker-compose.local.yml logs -f

# Specific service
docker compose -f docker-compose.local.yml logs -f backend
docker compose -f docker-compose.local.yml logs -f frontend
```

### Stop the Application

```bash
docker compose -f docker-compose.local.yml down
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.local.yml restart

# Restart specific service
docker compose -f docker-compose.local.yml restart backend
```

### Check Service Status

```bash
docker compose -f docker-compose.local.yml ps
```

### Import Additional Questions

```bash
docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py your_questions.xlsx
```

### Access Backend Shell

```bash
docker compose -f docker-compose.local.yml exec backend bash
```

### Access Database

```bash
docker compose -f docker-compose.local.yml exec postgres psql -U postgres -d quiz_db
```

## 🔧 Troubleshooting

### Issue: "Port already in use"

**Solution:** Stop the service using the port or change the port in `docker-compose.local.yml`

```bash
# Find what's using the port (example for port 3000)
# Windows
netstat -ano | findstr :3000

# Mac/Linux
lsof -i :3000
```

### Issue: "Docker daemon not running"

**Solution:** Start Docker Desktop application

### Issue: "Permission denied" (Linux/Mac)

**Solution:** Make the script executable

```bash
chmod +x setup.sh
```

### Issue: Services not starting

**Solution:** Check Docker logs

```bash
docker compose -f docker-compose.local.yml logs
```

### Issue: Frontend shows "Cannot connect to backend"

**Solution:**

1. Verify backend is running: http://localhost:8000/health
2. Check CORS settings in `.env`
3. Restart the backend: `docker compose -f docker-compose.local.yml restart backend`

### Issue: No questions appearing in quiz

**Solution:** Import questions manually

```bash
docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx
```

## 🎓 Using the Application

### For Students/Quiz Takers:

1. **Register an Account**

   - Navigate to http://localhost:3000
   - Click "Register" and create your account
   - Complete your profile (name, mobile number)

2. **Take a Quiz**

   - Browse available quizzes
   - Select a quiz and configure options (number of questions, difficulty)
   - Start the quiz and answer questions
   - View your results and explanations

3. **Check Leaderboard**
   - View your ranking
   - Filter by topic
   - See top performers

### For Administrators:

1. **Login as Admin**

   - Use credentials: `admin@example.com` / `Admin123!`

2. **Import Questions**

   - Prepare Excel file with questions (see template in docs)
   - Import via API or CLI:

   ```bash
   docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py questions.xlsx
   ```

3. **Manage Users**
   - Access admin endpoints at http://localhost:8000/docs
   - Use JWT token for authentication

## 📁 Project Structure

```
techxconf-quiz-app/
├── setup.ps1                 # Windows setup script
├── setup.sh                  # Mac/Linux setup script
├── QUICKSTART.md            # This file
├── docker-compose.local.yml # Local development configuration
├── .env                     # Environment variables (created by setup)
├── app/                     # Backend application
│   ├── api/                 # API endpoints
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   └── core/                # Core configuration
├── frontend/                # React frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   └── services/        # API client
│   └── Dockerfile.dev       # Frontend container
└── scripts/                 # Utility scripts
    └── import_xlsx.py       # Question import script
```

## 🔄 Development Workflow

### Making Code Changes

**Frontend Changes:**

- Edit files in `frontend/src/`
- Changes auto-reload in browser (hot reload enabled)

**Backend Changes:**

- Edit files in `app/`
- Server auto-restarts (development mode with `--reload`)

### Database Changes

1. Create migration:

```bash
docker compose -f docker-compose.local.yml exec backend alembic revision -m "description"
```

2. Edit migration file in `alembic/versions/`

3. Apply migration:

```bash
docker compose -f docker-compose.local.yml exec backend alembic upgrade head
```

## 📚 Additional Resources

- **Full Documentation:** See `README.md`
- **Deployment Guides:** See `DEPLOYMENT_GUIDE.md`
- **API Reference:** http://localhost:8000/docs (when running)
- **Troubleshooting:** See `LOCAL_DOCKER_SETUP.md`

## ✨ Features

- 🔐 **Secure Authentication** - JWT-based with refresh tokens
- 📝 **Dynamic Quizzes** - Customizable question count and difficulty
- ⏱️ **Timed Questions** - Configurable time limits
- 📊 **Real-time Leaderboards** - Topic-based and global rankings
- 📱 **Responsive Design** - Works on desktop and mobile
- 📥 **Excel Import** - Easy question management
- 🎯 **Detailed Results** - Question-by-question breakdown with explanations

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. View logs: `docker compose -f docker-compose.local.yml logs`
3. Verify all services are running: `docker compose -f docker-compose.local.yml ps`
4. Check health endpoint: http://localhost:8000/health

## 🎉 Next Steps

Once your application is running:

1. ✅ Register a user account
2. ✅ Take a sample quiz
3. ✅ Import your own questions
4. ✅ Explore the API documentation
5. ✅ Customize the application for your needs

Happy Quizzing! 🚀
