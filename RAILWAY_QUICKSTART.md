# Railway Deployment - Quick Start 🚂

## Method 1: Via Railway Dashboard (Easiest - Recommended)

### 5-Minute Deployment:

1. **Go to Railway**: https://railway.app
2. **Login** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `ramakishore-annalect/techxconf-quiz-app`
5. **Add Database**: Click "+ New" → "Database" → "Add PostgreSQL"
6. **Add Redis**: Click "+ New" → "Database" → "Add Redis"
7. **Set Variables** (in your web service → Variables tab):
   ```
   SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
   JWT_SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
   ENVIRONMENT=production
   DEBUG=False
   ```
8. **Generate Domain**: Settings → Networking → "Generate Domain"
9. **Deploy**: Railway auto-deploys!
10. **Run Migrations**: Install Railway CLI, then:
    ```bash
    npm i -g @railway/cli
    railway login
    railway link
    railway run alembic upgrade head
    ```

**Done! Your app is live! 🎉**

---

## Method 2: Via Automated Script

```bash
# Run the automated script
./deploy_railway.sh
```

Follow the interactive prompts!

---

## Method 3: Manual CLI Deployment

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add databases
railway add --database postgresql
railway add --database redis

# 5. Set environment variables
railway variables set SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
railway variables set JWT_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="False"

# 6. Deploy
railway up

# 7. Generate domain
railway domain

# 8. Run migrations
railway run alembic upgrade head

# 9. Import questions (optional)
railway run python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
```

---

## After Deployment

### Get Your App URL:
```bash
railway status
```

### View Logs:
```bash
railway logs
```

### Open Dashboard:
```bash
railway open
```

### Test Your App:
- **Frontend**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/docs`
- **Health Check**: `https://your-app.up.railway.app/health`

---

## Important Files Added:

- ✅ **`RAILWAY_DEPLOYMENT_GUIDE.md`** - Comprehensive guide
- ✅ **`railway.toml`** - Railway configuration
- ✅ **`deploy_railway.sh`** - Automated deployment script
- ✅ **`Dockerfile`** - Updated to use $PORT variable

---

## Cost: FREE! 💰

Railway provides **$5/month free credit** which is enough for development and small production apps!

---

## Need Help?

- **Full Guide**: See `RAILWAY_DEPLOYMENT_GUIDE.md`
- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway

---

**Recommended: Use Method 1 (Dashboard) for first deployment!**
