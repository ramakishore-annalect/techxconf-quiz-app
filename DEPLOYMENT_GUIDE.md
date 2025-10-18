# Deployment Guide - OGS-TechXConf Quiz App

## Pre-Deployment Checklist

### 1. Code Preparation
- [x] Application tested locally
- [x] 400 questions loaded in database
- [x] Timer system working (15 seconds per question)
- [x] TypeScript compilation successful
- [ ] Push code to GitHub repository

### 2. Configuration Updates Needed

#### Backend (`/app/core/config.py`)
```python
# Change from:
CORS_ORIGINS: List[str] = ["*"]

# To (after deployment):
CORS_ORIGINS: List[str] = [
    "https://your-frontend-domain.vercel.app",
    "https://your-custom-domain.com"  # if applicable
]
```

#### Frontend (`/frontend/.env.production`)
```bash
VITE_API_URL=https://your-backend-domain.railway.app/api/v1
```

---

## Deployment Options (Ranked by Ease & Cost)

### ⭐ OPTION 1: Railway.app (RECOMMENDED)
**Cost:** $5-10/month | **Difficulty:** ⭐⭐☆☆☆ Easy

#### Why Railway?
- One-click PostgreSQL database
- Automatic HTTPS/SSL
- Environment variable management
- Zero-config deployment
- Built-in monitoring
- Free $5 trial credit

#### Steps:

**1. Prepare Code**
```bash
# Initialize git (if not already)
cd /Users/ramakishore.nooji/Annalect\ Code/techxconf_quiz_app
git init
git add .
git commit -m "Initial commit - Production ready"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/techxconf-quiz-app.git
git branch -M main
git push -u origin main
```

**2. Deploy Backend to Railway**

a) Go to [railway.app](https://railway.app) and sign up
b) Click "New Project" → "Deploy from GitHub repo"
c) Select your repository
d) Railway will detect Dockerfile automatically
e) Add PostgreSQL:
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway automatically sets `DATABASE_URL`
f) Configure environment variables:
   ```
   SECRET_KEY=<generate-random-string>
   JWT_SECRET_KEY=<generate-another-random-string>
   ENVIRONMENT=production
   DEBUG=False
   QUESTION_TIME_LIMIT_SECONDS=15
   SESSION_EXPIRE_HOURS=48
   ```
g) Generate secrets:
   ```bash
   # Run locally to generate secure keys
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
h) Click "Deploy" - Railway will build and deploy
i) Note your backend URL: `https://your-service.railway.app`

**3. Run Database Migration**
```bash
# In Railway's service settings, go to "Variables" tab
# Add temporary variable for migration:
PYTHONPATH=/app

# Then run one-time command in Railway's terminal:
alembic upgrade head
```

**4. Import Questions to Production Database**
```bash
# From Railway service terminal or run locally with production DATABASE_URL
python scripts/import_xlsx.py Cloud_AI_Quiz_400.xlsx --mode replace
```

**5. Deploy Frontend to Vercel**

a) Go to [vercel.com](https://vercel.com) and sign up
b) Click "New Project" → Import your GitHub repo
c) Set root directory: `frontend`
d) Framework preset: Vite
e) Build command: `npm run build`
f) Output directory: `dist`
g) Environment variables:
   ```
   VITE_API_URL=https://your-service.railway.app/api/v1
   ```
h) Click "Deploy"
i) Note your frontend URL: `https://your-app.vercel.app`

**6. Update CORS in Backend**
- Go back to Railway
- Update `CORS_ORIGINS` environment variable:
  ```
  CORS_ORIGINS=["https://your-app.vercel.app"]
  ```
- Redeploy backend

**7. Test Production**
- Visit `https://your-app.vercel.app`
- Register a new user
- Start a quiz
- Verify timer works (15 seconds)
- Complete quiz and check results

**Total Cost:** ~$5-10/month (Railway) + $0 (Vercel free tier)

---

### OPTION 2: Render.com (Free Tier Available)
**Cost:** Free (with limitations) | **Difficulty:** ⭐⭐⭐☆☆ Medium

#### Limitations:
- Free tier spins down after 15 mins of inactivity (cold start ~30-60s)
- 750 hours/month free compute
- PostgreSQL limited to 90 days then $7/month

#### Steps:

**1. Deploy Backend**
a) Go to [render.com](https://render.com) and sign up
b) Click "New +" → "Web Service"
c) Connect GitHub repository
d) Settings:
   - Name: `techxconf-quiz-backend`
   - Environment: Docker
   - Build command: (auto-detected from Dockerfile)
   - Start command: (auto-detected)
   - Plan: Free
e) Add PostgreSQL:
   - Click "New +" → "PostgreSQL"
   - Name: `techxconf-quiz-db`
   - Plan: Free
   - Note the internal database URL
f) Environment variables:
   ```
   DATABASE_URL=<from-postgresql-service>
   SECRET_KEY=<generate>
   JWT_SECRET_KEY=<generate>
   ENVIRONMENT=production
   DEBUG=False
   QUESTION_TIME_LIMIT_SECONDS=15
   SESSION_EXPIRE_HOURS=48
   ```
g) Click "Create Web Service"
h) Note URL: `https://techxconf-quiz-backend.onrender.com`

**2. Run Migrations**
```bash
# From Render's shell (service → Shell tab)
alembic upgrade head
python scripts/import_xlsx.py Cloud_AI_Quiz_400.xlsx --mode replace
```

**3. Deploy Frontend to Render**
a) Click "New +" → "Static Site"
b) Connect same GitHub repo
c) Settings:
   - Name: `techxconf-quiz-frontend`
   - Root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
d) Environment variables:
   ```
   VITE_API_URL=https://techxconf-quiz-backend.onrender.com/api/v1
   ```
e) Deploy

**4. Update CORS**
- Update backend environment variable
- Redeploy backend service

**Total Cost:** Free (first 90 days), then ~$7/month for database

---

### OPTION 3: 100% Free Tier Combo
**Cost:** $0 | **Difficulty:** ⭐⭐⭐⭐☆ Advanced

#### Stack:
- **Frontend:** Vercel (Free)
- **Database:** Supabase (Free - 500MB)
- **Backend:** PythonAnywhere (Free - limited)

#### Limitations:
- PythonAnywhere free tier: Limited CPU, no custom domains
- Supabase free tier: 500MB storage, 2GB bandwidth
- Not suitable for high traffic

#### Steps:

**1. Setup Supabase Database**
a) Go to [supabase.com](https://supabase.com)
b) Create new project
c) Wait for database provisioning
d) Go to Settings → Database
e) Note connection string:
   ```
   postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
   ```

**2. Deploy Backend to PythonAnywhere**
a) Sign up at [pythonanywhere.com](https://pythonanywhere.com)
b) Go to "Web" tab → "Add a new web app"
c) Choose "Manual configuration" → Python 3.10
d) Upload code:
   ```bash
   # From local machine
   git clone https://github.com/YOUR_USERNAME/techxconf-quiz-app.git
   ```
e) Create virtual environment:
   ```bash
   cd techxconf-quiz-app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
f) Configure WSGI file (edit in PythonAnywhere):
   ```python
   import sys
   path = '/home/YOUR_USERNAME/techxconf-quiz-app'
   if path not in sys.path:
       sys.path.append(path)
   
   from app.main import app as application
   ```
g) Set environment variables in web app settings
h) Reload web app

**3. Deploy Frontend to Vercel**
(Same as Option 1, step 5)

**Total Cost:** $0 (all free tiers)

---

### OPTION 4: Google Cloud Run (Pay-as-you-go)
**Cost:** ~$0-5/month | **Difficulty:** ⭐⭐⭐⭐☆ Advanced

#### Benefits:
- Generous free tier (2 million requests/month)
- Auto-scaling (scales to zero)
- Only pay for usage

#### Quick Start:

**1. Install Google Cloud SDK**
```bash
brew install --cask google-cloud-sdk
gcloud init
```

**2. Build and Push Docker Image**
```bash
# Set project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/techxconf-quiz

# Deploy
gcloud run deploy techxconf-quiz \
  --image gcr.io/YOUR_PROJECT_ID/techxconf-quiz \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SECRET_KEY=xxx,ENVIRONMENT=production
```

**3. Setup Cloud SQL PostgreSQL**
```bash
gcloud sql instances create quiz-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Connect Cloud Run to Cloud SQL
gcloud run services update techxconf-quiz \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:quiz-db
```

**4. Deploy Frontend**
(Use Vercel as in previous options)

**Total Cost:** ~$0-5/month (within free tier for moderate usage)

---

## Post-Deployment Tasks

### 1. Update CORS
Update `/app/core/config.py` with your frontend domain

### 2. Custom Domain (Optional)
- **Vercel:** Project Settings → Domains → Add custom domain
- **Railway:** Service Settings → Networking → Custom domain
- Configure DNS records (A/CNAME) as instructed

### 3. Monitoring Setup
- **Railway:** Built-in metrics (CPU, Memory, Requests)
- **Render:** Dashboard metrics
- **Google Cloud:** Cloud Monitoring

### 4. SSL Certificate
✅ All platforms provide automatic HTTPS/SSL

### 5. Database Backups
- **Railway:** Automatic backups (paid plans)
- **Render:** Automatic backups
- **Supabase:** Daily backups (free tier)

---

## Testing Production Deployment

### Health Checks
```bash
# Backend health
curl https://your-backend-domain.com/health

# API test
curl https://your-backend-domain.com/api/v1/quizzes/
```

### Functionality Tests
1. Register new user
2. Login
3. View available quizzes
4. Start quiz
5. Answer questions (verify 15-second timer)
6. Submit quiz
7. View results (verify skipped questions shown)
8. Check leaderboard

---

## Troubleshooting

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend domain
- Check for trailing slashes mismatch
- Ensure protocol matches (https/http)

### Database Connection Issues
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
- Check database firewall rules
- Run migrations: `alembic upgrade head`

### Timer Not Working
- Clear browser cache
- Check browser console for errors
- Verify API returns `time_limit_seconds` field

### Questions Not Loading
- Verify import script ran successfully
- Check database: `SELECT COUNT(*) FROM questions;`
- Ensure user has permission to access quizzes

---

## Recommended Choice

**For your use case (quiz app with 400 questions, minimal cost):**

🎯 **Railway.app + Vercel** (Option 1)

**Reasons:**
1. ✅ Easiest setup (< 30 mins)
2. ✅ Reliable (no cold starts)
3. ✅ Affordable ($5-10/month)
4. ✅ Automatic HTTPS
5. ✅ Easy scaling
6. ✅ Built-in PostgreSQL
7. ✅ Good for production use

**Start here, upgrade later if needed.**

---

## Next Steps

1. Push code to GitHub
2. Sign up for Railway.app
3. Follow "Option 1" steps above
4. Deploy in 20-30 minutes
5. Share quiz URL with colleagues! 🚀

Good luck with your deployment! 🎉
