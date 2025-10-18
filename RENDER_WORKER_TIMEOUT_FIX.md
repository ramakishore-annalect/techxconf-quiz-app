# 🔴 Render Worker Timeout - Troubleshooting Guide

## ❌ Error You're Seeing:

```
[2025-10-18 10:50:08 +0000] [7] [CRITICAL] WORKER TIMEOUT (pid:63)
[2025-10-18 10:50:08 +0000] [7] [ERROR] Worker (pid:66) was sent SIGKILL! Perhaps out of memory?
```

## 🔍 What This Means:

Your FastAPI app is **failing to start** within 30 seconds (default gunicorn timeout), causing workers to be killed.

---

## 🚨 Root Causes (Most Likely):

### 1. **Missing Environment Variables** (90% of cases)
- `DATABASE_URL` not set
- `REDIS_URL` not set
- App hangs trying to connect to databases that don't exist

### 2. **Database Not Connected**
- PostgreSQL service not added to Render
- Or not linked to your web service

### 3. **Wrong DATABASE_URL Format**
- Render uses `postgres://` (not `postgresql://`)
- FastAPI async needs `postgresql+asyncpg://`

### 4. **Memory Limits**
- Render free tier has 512MB RAM limit
- 4 gunicorn workers × memory = out of memory

---

## ✅ Fixes (Apply in Order):

### Fix 1: Check Environment Variables

**Go to Render Dashboard → Your Service → Environment:**

Required variables:
```bash
DATABASE_URL=<provided by PostgreSQL service>
REDIS_URL=<provided by Redis service>
SECRET_KEY=<generate new>
JWT_SECRET_KEY=<generate new>
ENVIRONMENT=production
DEBUG=False
```

**⚠️ IMPORTANT**: If `DATABASE_URL` is missing or wrong, your app will hang!

---

### Fix 2: Add PostgreSQL Database

If you haven't added a database yet:

1. **In Render Dashboard**, click **"New +"** → **"PostgreSQL"**
2. Name it: `techxconf-quiz-db`
3. Wait for it to provision (2-3 minutes)
4. **Copy the Internal Database URL** (important!)
5. Add to your web service environment variables:
   ```
   DATABASE_URL=<paste internal URL here>
   ```

**Note**: Use **Internal URL** (not External) for better performance and security!

---

### Fix 3: Add Redis (Optional but Recommended)

1. **In Render Dashboard**, click **"New +"** → **"Redis"**
2. Name it: `techxconf-quiz-redis`
3. Wait for it to provision
4. **Copy the Internal Redis URL**
5. Add to your web service:
   ```
   REDIS_URL=<paste internal URL here>
   ```

---

### Fix 4: Reduce Worker Count (Memory Issue)

**In Render Dashboard → Your Service → Settings:**

Change the start command to use fewer workers:

```bash
gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 2 --timeout 120 --bind 0.0.0.0:$PORT app.main:app
```

**Changes:**
- `--workers 2` (down from 4) - Uses less memory
- `--timeout 120` - Gives more time to connect to database

---

### Fix 5: Update DATABASE_URL Format

Render provides `postgres://` but SQLAlchemy async needs `postgresql+asyncpg://`.

**Option A: Let the app auto-convert** (already done in config.py)

**Option B: Manually set it in Render:**

If Render provides:
```
postgres://user:pass@host:5432/db
```

Change it to:
```
postgresql+asyncpg://user:pass@host:5432/db
```

---

### Fix 6: Verify Database Is Ready

**In Render Dashboard → PostgreSQL service:**

- Status should be **"Available"** (green)
- If it says **"Creating"** (yellow), wait for it to finish

---

### Fix 7: Check Dockerfile Port

Make sure your Dockerfile exposes the right port:

```dockerfile
EXPOSE 8000
CMD gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 2 --timeout 120 --bind 0.0.0.0:${PORT:-8000} app.main:app
```

---

## 🔧 Updated Startup (Already Applied)

I've updated your `app/main.py` to:
- ✅ Handle database connection failures gracefully
- ✅ Continue running even if DB/Redis fail
- ✅ Log errors instead of crashing

This means your app will **start successfully** even if databases aren't connected yet, then you can fix the connection issues.

---

## 📋 Step-by-Step Checklist

### On Render Dashboard:

1. **Check PostgreSQL Service**
   - [ ] PostgreSQL service created and **"Available"**
   - [ ] Copy **Internal Database URL**

2. **Check Redis Service** (optional)
   - [ ] Redis service created and **"Available"**
   - [ ] Copy **Internal Redis URL**

3. **Check Web Service Environment Variables**
   - [ ] `DATABASE_URL` = PostgreSQL internal URL
   - [ ] `REDIS_URL` = Redis internal URL (if using)
   - [ ] `SECRET_KEY` = random secure string
   - [ ] `JWT_SECRET_KEY` = random secure string
   - [ ] `ENVIRONMENT` = `production`
   - [ ] `DEBUG` = `False`

4. **Update Start Command** (if memory issues)
   - [ ] Reduce workers from 4 to 2
   - [ ] Increase timeout from 30 to 120 seconds

5. **Redeploy**
   - [ ] Click "Manual Deploy" → "Clear build cache & deploy"

---

## 🧪 How to Test

### After fixing, you should see in logs:

**✅ Success:**
```
[INFO] Starting application app_name=Quiz Backend API
[INFO] Database initialized
[INFO] Redis initialized
[INFO] Application startup complete
[INFO] Booting worker with pid: 7
```

**⚠️ Partial Success (DB not connected but app runs):**
```
[WARNING] Database initialization failed: ...
[INFO] App will continue without database
[INFO] Application startup complete
```

---

## 🚀 Quick Fix Commands

### Generate Secure Keys (run locally):
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Check If Services Are Running (in Render Shell):
```bash
# Test database connection
python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"

# Test Redis connection
python -c "from app.core.redis import get_redis; import asyncio; r = asyncio.run(get_redis()); print(asyncio.run(r.ping()))"
```

---

## 🆘 Still Not Working?

### Check Render Logs for Specific Errors:

1. **"could not translate host name"** → DATABASE_URL is wrong
2. **"FATAL: password authentication failed"** → Database credentials wrong
3. **"Connection refused"** → Database service not running
4. **"Out of memory"** → Reduce worker count to 1

### Get Help:

- **Render Discord**: https://discord.gg/render
- **Render Docs**: https://render.com/docs
- **Database Logs**: Check PostgreSQL service logs separately

---

## 📝 Most Common Solution:

**90% of the time, the issue is missing `DATABASE_URL`.**

1. ✅ Add PostgreSQL service in Render
2. ✅ Copy Internal Database URL
3. ✅ Add `DATABASE_URL` to web service environment
4. ✅ Redeploy

---

**Your app startup is now more resilient! Check Render logs after redeploying.** 🚀
