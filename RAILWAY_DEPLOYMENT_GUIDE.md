# Railway.app Deployment Guide - TechXConf Quiz App

## 🚂 Complete Guide to Deploy Your Quiz App on Railway

Railway.app is a modern platform that makes deploying full-stack applications incredibly easy. It supports Docker, provides managed PostgreSQL and Redis, and offers automatic deployments from GitHub.

---

## 📋 Prerequisites

- ✅ GitHub repository created (you already have this!)
- ✅ Railway.app account (free tier available)
- ✅ Your app uses Docker (you have docker-compose.yml)

---

## 🎯 Method 1: Deploy from GitHub (Recommended)

This method connects Railway to your GitHub repository for automatic deployments.

### Step 1: Sign Up for Railway

1. Go to **https://railway.app**
2. Click **"Login"** or **"Start a New Project"**
3. Sign in with **GitHub** (recommended for easy integration)
4. Authorize Railway to access your GitHub account

### Step 2: Create a New Project

1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. You'll see a list of your repositories (including private ones)
4. Select **`techxconf-quiz-app`**

Railway will automatically detect your Docker configuration!

### Step 3: Add PostgreSQL Database

Your app needs PostgreSQL, so let's add it:

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will create a managed PostgreSQL instance
4. Note: Railway automatically creates a `DATABASE_URL` variable

### Step 4: Add Redis

Your app also needs Redis:

1. Click **"+ New"** again
2. Select **"Database"** → **"Add Redis"**
3. Railway will create a managed Redis instance
4. Note: Railway automatically creates a `REDIS_URL` variable

### Step 5: Configure Environment Variables

Click on your **main service** (the web app), then go to **"Variables"** tab:

```bash
# Application Settings
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this
ENVIRONMENT=production
DEBUG=False

# Frontend URL (will be provided by Railway after first deploy)
FRONTEND_URL=https://your-app.up.railway.app

# Backend/API Settings
ALLOWED_HOSTS=your-app.up.railway.app
CORS_ORIGINS=https://your-app.up.railway.app

# Database (Railway provides this automatically)
# DATABASE_URL is already set by the PostgreSQL service

# Redis (Railway provides this automatically)
# REDIS_URL is already set by the Redis service
```

**Important**: Generate secure keys for production:

```bash
# Run these locally to generate secure keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the output for `SECRET_KEY` and `JWT_SECRET_KEY`.

### Step 6: Configure Service Settings

1. In your service settings, find **"Deploy"** section
2. **Root Directory**: Leave as `/` (default)
3. **Dockerfile Path**: Should auto-detect `Dockerfile`
4. **Port**: Railway will auto-detect port from your Dockerfile (usually 8000)

### Step 7: Deploy!

1. Click **"Deploy"** or wait for automatic deployment
2. Railway will:
   - Clone your GitHub repo
   - Build the Docker image
   - Run database migrations (if configured)
   - Start your application
3. Watch the **"Deployments"** tab for build logs

### Step 8: Get Your Public URL

1. Go to **"Settings"** tab of your web service
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Railway will give you a URL like: `https://techxconf-quiz-app.up.railway.app`

### Step 9: Update Frontend URL

1. Go back to **"Variables"** tab
2. Update `FRONTEND_URL` with the Railway-generated domain
3. Update `CORS_ORIGINS` with the same domain
4. Redeploy (Railway will auto-redeploy on variable changes)

### Step 10: Run Database Migrations

You need to run migrations to create database tables:

**Option A: Use Railway CLI** (recommended)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run alembic upgrade head
```

**Option B: Add to Dockerfile**

Your Dockerfile should already have migration commands, but verify:

```dockerfile
# Make sure your Dockerfile has this before starting the server
RUN alembic upgrade head
```

### Step 11: Import Quiz Questions

After deployment, import your questions:

```bash
# Using Railway CLI
railway run python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
```

Or upload the Excel file to your deployed instance via an admin endpoint (if you create one).

---

## 🎯 Method 2: Deploy via Railway CLI (Alternative)

If you prefer command-line deployment:

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

This opens a browser for authentication.

### Step 3: Initialize Railway Project

```bash
cd /Users/ramakishore.nooji/Annalect\ Code/techxconf_quiz_app

railway init
```

Follow the prompts:
- Project name: `techxconf-quiz-app`
- Select: "Empty Project"

### Step 4: Add PostgreSQL

```bash
railway add --database postgresql
```

### Step 5: Add Redis

```bash
railway add --database redis
```

### Step 6: Set Environment Variables

```bash
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set JWT_SECRET_KEY="your-jwt-secret-key-here"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="False"
```

### Step 7: Deploy

```bash
railway up
```

Railway will:
- Build your Docker image
- Push to Railway
- Deploy your application

### Step 8: Get Domain

```bash
railway domain
```

This generates a public URL for your app.

---

## 🔧 Railway.toml Configuration (Optional)

Create a `railway.toml` file in your project root for advanced configuration:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

---

## 🗄️ Database Setup Checklist

After deployment, verify database is set up:

### 1. Check Database Connection

```bash
railway run python -c "from app.core.database import engine; print(engine.url)"
```

### 2. Run Migrations

```bash
railway run alembic upgrade head
```

### 3. Import Questions

```bash
# Upload your Excel file first, then:
railway run python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
```

### 4. Create Admin User (Optional)

```bash
railway run python scripts/create_admin.py
```

---

## 📊 Railway Project Structure

Your Railway project will have 3 services:

```
techxconf-quiz-app (Project)
├── 🐳 web (Your FastAPI + React app)
│   └── Environment Variables
├── 🐘 PostgreSQL (Database)
│   └── DATABASE_URL (auto-linked)
└── 🔴 Redis (Cache)
    └── REDIS_URL (auto-linked)
```

---

## 💰 Railway Pricing

- **Hobby Plan** (Free):
  - $5 monthly credit
  - Enough for small apps
  - Auto-sleep after inactivity

- **Developer Plan** ($5/month):
  - $5 credit + pay for usage
  - No auto-sleep
  - Better for production

- **Team Plan** ($20/month):
  - $20 credit + pay for usage
  - Collaboration features
  - Priority support

**Your app will likely fit in the free tier during development!**

---

## 🔍 Monitoring Your Deployment

### View Logs

```bash
# Using CLI
railway logs

# Or in Railway Dashboard
# Go to "Deployments" → Click on latest deployment → View logs
```

### Check Service Health

```bash
# Test your API
curl https://your-app.up.railway.app/api/v1/health

# Check database connection
railway run python -c "from app.core.database import SessionLocal; print('DB Connected!')"
```

### Monitor Resources

- Go to Railway Dashboard
- Click on your service
- View **"Metrics"** tab for:
  - CPU usage
  - Memory usage
  - Network traffic
  - Request count

---

## 🔐 Security Best Practices

### 1. Use Strong Secret Keys

```bash
# Generate secure keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### 2. Set DEBUG=False in Production

```bash
railway variables set DEBUG="False"
```

### 3. Configure CORS Properly

```bash
railway variables set CORS_ORIGINS="https://your-app.up.railway.app"
```

### 4. Use Environment-Specific Settings

Your `app/core/config.py` should already handle this, but verify:

```python
class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
```

---

## 🚀 Automatic Deployments

### Enable GitHub Auto-Deploy

Railway automatically deploys when you push to GitHub!

1. Every `git push` to `main` triggers a new deployment
2. Railway builds and deploys automatically
3. If build fails, previous version stays running

### Deploy from Specific Branch

1. Go to Railway service settings
2. Find **"Source"** section
3. Change branch from `main` to your preferred branch

---

## 🔄 Update Your App

When you make changes:

```bash
# Make changes locally
git add .
git commit -m "Update: Added new feature"
git push origin main

# Railway automatically deploys!
# Watch deployment in Railway Dashboard
```

---

## 🆘 Troubleshooting

### Problem: Build Fails

**Solution**: Check build logs in Railway Dashboard

```bash
# Common issues:
# 1. Missing dependencies in requirements.txt
# 2. Incorrect Dockerfile syntax
# 3. Port mismatch

# Check logs
railway logs --deployment <deployment-id>
```

### Problem: Database Connection Error

**Solution**: Verify DATABASE_URL is set

```bash
# Check variables
railway variables

# Test connection
railway run python -c "import psycopg2; print('Connected!')"
```

### Problem: Application Won't Start

**Solution**: Check if port is correctly exposed

```bash
# Railway expects your app to listen on $PORT
# Verify in your Dockerfile:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

### Problem: Frontend Can't Connect to Backend

**Solution**: Update CORS settings

```bash
railway variables set CORS_ORIGINS="https://your-app.up.railway.app"
```

### Problem: Database Tables Don't Exist

**Solution**: Run migrations

```bash
railway run alembic upgrade head
```

---

## 📱 Access Your Deployed App

After successful deployment:

1. **Frontend**: `https://your-app.up.railway.app`
2. **API Docs**: `https://your-app.up.railway.app/docs`
3. **Health Check**: `https://your-app.up.railway.app/api/v1/health`

---

## 🎯 Complete Deployment Checklist

- [ ] Railway account created
- [ ] Project created from GitHub repo
- [ ] PostgreSQL database added
- [ ] Redis database added
- [ ] Environment variables configured
- [ ] Public domain generated
- [ ] Database migrations run
- [ ] Quiz questions imported
- [ ] CORS settings updated
- [ ] Application accessible via URL
- [ ] API documentation working
- [ ] Login/Register working
- [ ] Quizzes loading correctly
- [ ] Leaderboard displaying

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app
- **Railway CLI Docs**: https://docs.railway.app/develop/cli
- **Railway Discord**: https://discord.gg/railway
- **Your Deployed App**: `https://your-app.up.railway.app` (after deployment)

---

## 📞 Need Help?

- **Railway Discord**: Join for community support
- **Railway Docs**: Comprehensive documentation
- **GitHub Issues**: Report bugs in Railway's GitHub repo

---

**Ready to deploy? Follow Method 1 step-by-step! 🚀**

---

## 🎉 Post-Deployment

After successful deployment, you can:

1. **Share your app** with the team
2. **Monitor usage** in Railway dashboard
3. **Set up custom domain** (optional, paid feature)
4. **Enable notifications** for deployment status
5. **Invite team members** to collaborate

Your OGS TechXConf Quiz App is now live and accessible worldwide! 🌍
