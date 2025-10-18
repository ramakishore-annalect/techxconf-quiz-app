# Render.com Deployment Guide - TechXConf Quiz App

## 🚀 Why Render?
- Free tier for web services
- Native Docker support
- Managed PostgreSQL & Redis
- Auto-deploy from GitHub (private repos supported)
- Free SSL

---

## 📋 Prerequisites
- GitHub repo ready (private or public)
- Dockerfile in project root
- requirements.txt in project root
- Database migrations (alembic)

---

## 🎯 Step-by-Step Deployment

### 1. Sign Up & Connect GitHub
- Go to https://dashboard.render.com/
- Sign up (or log in)
- Click "New Web Service"
- Choose "Connect a repository"
- Authorize Render to access your GitHub (private repos supported)
- Select your repo: `ramakishore-annalect/techxconf-quiz-app`

### 2. Configure Web Service
- **Environment**: Docker
- **Root Directory**: `/` (project root)
- **Dockerfile Path**: `Dockerfile`
- **Start Command**: Leave blank (Dockerfile CMD is used)
- **Port**: 8000 (Render auto-detects from Dockerfile)

### 3. Add Environment Variables
- Click "Environment" tab
- Add these variables:
  ```
  SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
  JWT_SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
  ENVIRONMENT=production
  DEBUG=False
  # Render will provide DATABASE_URL and REDIS_URL automatically if you add those services
  ```

### 4. Add PostgreSQL Database
- Go to "New" → "PostgreSQL"
- Name your database
- Render will create a managed instance
- Copy the `DATABASE_URL` and add it to your web service's environment variables

### 5. Add Redis (Optional)
- Go to "New" → "Redis"
- Name your Redis instance
- Copy the `REDIS_URL` and add it to your web service's environment variables

### 6. Deploy!
- Click "Manual Deploy" or push to GitHub (auto-deploy enabled)
- Watch build logs for errors
- If you see `TypeError: argument 'port': 'str' object cannot be interpreted as an integer`, you are now FIXED!

### 7. Run Database Migrations
- Open Render Shell (or use SSH)
- Run:
  ```bash
  alembic upgrade head
  ```

### 8. Import Quiz Questions
- Upload your Excel file to the instance (via shell or admin endpoint)
- Run:
  ```bash
  python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
  ```

---

## 📝 Notes
- Render auto-detects Dockerfile and builds your app
- Free HTTPS domain provided (e.g. `https://techxconf-quiz-app.onrender.com`)
- Managed databases are billed after free trial
- You can scale vertically/horizontally easily

---

## 🆘 Troubleshooting
- **Build fails**: Check Dockerfile, requirements.txt, and logs
- **Database connection error**: Verify `DATABASE_URL` is set and correct
- **App not starting**: Check port exposure in Dockerfile (`EXPOSE 8000`)
- **Frontend can't connect to backend**: Set correct CORS_ORIGINS
- **Migrations not run**: Run `alembic upgrade head` in shell

---

## 📞 Support
- Render Docs: https://render.com/docs
- Discord: https://render.com/community
- Email: support@render.com

---

**Your app is now ready for production on Render! 🚀**
