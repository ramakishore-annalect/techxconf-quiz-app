# 🎯 OGS TechXConf Quiz Application

A modern, full-stack quiz platform built for technical assessments and knowledge validation. Features a FastAPI backend with PostgreSQL, React/TypeScript frontend, and comprehensive quiz management capabilities.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## ✨ Features

### 🎮 Quiz Management
- **428 Curated Questions** across 9 technical topics
- **Smart Question Selection** with difficulty mixing (Easy/Medium/Hard)
- **15-Second Timer** per question with auto-advance
- **No Duplicate Questions** in a session (database-enforced unique constraint)
- **Multiple Quiz Attempts** with different question sets

### 📊 Topics Covered
- **AI** (49 questions) - Artificial Intelligence fundamentals
- **AI Agents** (49 questions) - Agent architectures and safety
- **AWS** (50 questions) - Amazon Web Services
- **Azure** (50 questions) - Microsoft Azure
- **GCP** (30 questions) - Google Cloud Platform
- **Git** (50 questions) - Version control
- **ML** (50 questions) - Machine Learning
- **Python** (50 questions) - Python programming
- **Relational Databases** (50 questions) - SQL and database concepts

### 🏆 User Experience
- **Real-time Leaderboard** with scoring and rankings
- **Instant Feedback** showing correct answers and explanations
- **Progress Tracking** across all attempted quizzes
- **Responsive Design** works on desktop, tablet, and mobile
- **User Profiles** with quiz history and statistics

### 🔐 Security & Authentication
- **JWT-based Authentication** with refresh tokens
- **Role-based Access** (public quizzes vs authenticated)
- **Secure Password Storage** with bcrypt hashing
- **Session Management** with Redis caching
- **CORS Protection** configured for production

### 🎨 Modern UI/UX
- **Tailwind CSS** for styling
- **Lucide Icons** for consistent iconography
- **Color-coded Timer** (red/orange/gray based on time remaining)
- **Responsive Layout** with mobile-first design
- **OGS Branding** with custom logo

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React/TS      │────▶│   FastAPI       │────▶│   PostgreSQL    │
│   Frontend      │     │   Backend       │     │   Database      │
│   (Port 3000)   │     │   (Port 8000)   │     │   (Port 5432)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │     Redis       │
                        │  Cache/Session  │
                        │   (Port 6379)   │
                        └─────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI (Python 3.11) - High-performance async API framework
- SQLAlchemy - ORM with async support
- Alembic - Database migrations
- PostgreSQL 15 - Primary database
- Redis 7 - Caching and session storage
- Celery - Async task processing
- Pydantic - Data validation

**Frontend:**
- React 18 - UI library
- TypeScript - Type safety
- Vite - Build tool and dev server
- Tailwind CSS - Utility-first styling
- React Router - Client-side routing
- Axios - HTTP client
- React Hook Form - Form management

**DevOps:**
- Docker & Docker Compose - Containerization
- Prometheus - Metrics collection
- Grafana - Monitoring dashboards
- Nginx - Reverse proxy (optional)

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Mac/Windows) or Docker + Docker Compose (Linux)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/techxconf-quiz-app.git
cd techxconf-quiz-app
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://quiz_user:quiz_password@db:5432/quiz_db
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=quiz_password
POSTGRES_DB=quiz_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Application
ENVIRONMENT=development
DEBUG=True
QUESTION_TIME_LIMIT_SECONDS=15
SESSION_EXPIRE_HOURS=48
```

Create `frontend/.env`:

```bash
echo "VITE_API_URL=http://localhost:8000/api/v1" > frontend/.env
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Check services are running
docker-compose ps
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec web alembic upgrade head

# Import questions (optional - 428 questions included)
docker-compose exec web python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### 6. Create Your First User

Visit http://localhost:3000 and click "Register" to create an account, or use the API:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "display_name": "Test User"
  }'
```

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment options
- [GitHub Upload Guide](GITHUB_UPLOAD_GUIDE.md) - How to push to GitHub
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (Swagger)
- [Database Refresh Guide](DATABASE_REFRESH_FINAL_2025-10-18.md) - Question management

## 🎮 Usage

### Taking a Quiz

1. **Register/Login** at http://localhost:3000
2. **Browse Quizzes** on the home page
3. **Select a Topic** (e.g., Python, AWS, AI)
4. **Configure Quiz**:
   - Number of questions (1-50)
   - Difficulty mix (Easy/Medium/Hard percentages)
5. **Start Quiz** - 15 seconds per question
6. **View Results** with correct answers and explanations
7. **Check Leaderboard** to see your ranking

### Admin Tasks

```bash
# Import new questions from Excel
docker-compose exec web python scripts/import_xlsx.py your_questions.xlsx --mode replace

# Run database migrations
docker-compose exec web alembic upgrade head

# Create a new migration
docker-compose exec web alembic revision -m "your_migration_name"

# Remove duplicate questions
docker-compose exec web python scripts/remove_duplicates.py

# View database directly
docker-compose exec db psql -U quiz_user -d quiz_db
```

## 🧪 Testing

```bash
# Run backend tests
docker-compose exec web pytest tests/

# Run frontend tests
cd frontend
npm run test

# Run with coverage
docker-compose exec web pytest --cov=app tests/
```

## 📊 Monitoring

Access monitoring dashboards:

- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin` (change in production)

- **Prometheus**: http://localhost:9090
  - View metrics and targets

## 🔧 Development

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (without Docker)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Format
npm run format
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `app` | 8000 | FastAPI backend |
| `frontend` | 3000 | React development server |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache |
| `celery_worker` | - | Async task processor |
| `celery_beat` | - | Periodic task scheduler |
| `prometheus` | 9090 | Metrics collector |
| `grafana` | 3001 | Monitoring dashboard |

## 🗂️ Project Structure

```
techxconf-quiz-app/
├── app/                        # Backend application
│   ├── api/                    # API routes
│   │   └── api_v1/            
│   │       ├── api.py         # API router
│   │       └── endpoints/     # Endpoint modules
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings
│   │   ├── database.py        # Database connection
│   │   ├── auth.py            # Authentication
│   │   └── redis.py           # Redis connection
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   └── utils/                  # Utilities
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # Context providers
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utility functions
│   └── public/                # Static assets
├── alembic/                    # Database migrations
├── scripts/                    # Utility scripts
├── tests/                      # Test files
├── monitoring/                 # Monitoring config
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Backend container
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚢 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions for:

- Railway.app (Recommended - $5-10/month)
- Render.com (Free tier available)
- Vercel + Supabase + PythonAnywhere (100% free)
- Google Cloud Run (Pay-as-you-go)

### Quick Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

## 🔐 Security Considerations

- ✅ JWT tokens with refresh mechanism
- ✅ Password hashing with bcrypt
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Environment variable management
- ✅ Input validation (Pydantic)
- ⚠️ **Change default secrets in production**
- ⚠️ **Use HTTPS in production**
- ⚠️ **Configure CORS with specific origins**

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript/React
- Write tests for new features
- Update documentation as needed

## 📝 License

This project is proprietary software developed for OGS TechXConf.

## 👥 Authors

- **Ramakishore Nooji** - Initial development
- **OGS Team** - Requirements and design

## 🙏 Acknowledgments

- FastAPI for the excellent async framework
- React team for the amazing UI library
- PostgreSQL for reliable data storage
- Tailwind CSS for rapid UI development
- The open-source community

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact: [your.email@ogs.com](mailto:your.email@ogs.com)
- Documentation: See `DEPLOYMENT_GUIDE.md`

## 🗺️ Roadmap

- [ ] Add question difficulty adaptation based on user performance
- [ ] Implement quiz categories and tags
- [ ] Add team/group quiz competitions
- [ ] Create mobile app (React Native)
- [ ] Add analytics dashboard for administrators
- [ ] Implement question versioning
- [ ] Add multi-language support
- [ ] Create question authoring interface

## 📊 Statistics

- **428 Questions** across 9 topics
- **3 Difficulty Levels** per topic
- **15-Second Timer** per question
- **Zero Duplicates** (database-enforced)
- **Full Test Coverage** (backend)

---

**Built with ❤️ for OGS TechXConf 2025**
