# Full-Stack Deployment Options

## 🎯 Your Current Situation

Your app has:
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite
- **Databases**: PostgreSQL + Redis

---

## ✅ Option 1: Single Docker Image (Full-Stack) - RECOMMENDED ⭐

**Deploy both frontend and backend in ONE Docker container.**

### Pros:
- ✅ One deployment, one service, one URL
- ✅ Cheaper (single instance)
- ✅ FastAPI serves React frontend
- ✅ No CORS issues
- ✅ Easiest to manage

### Cons:
- ❌ Frontend and backend scale together (not independently)

### Files Created:
- ✅ `Dockerfile.fullstack` - Builds both frontend and backend
- ✅ `app/main.py` - Updated to serve React static files

### How to Deploy on Render:
1. **Rename Dockerfile**:
   ```bash
   mv Dockerfile Dockerfile.backend-only
   mv Dockerfile.fullstack Dockerfile
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add full-stack Docker deployment"
   git push origin main
   ```

3. **Deploy on Render**:
   - Go to https://dashboard.render.com/
   - Create "New Web Service" from your repo
   - Environment: **Docker**
   - Render auto-detects `Dockerfile`
   - Add PostgreSQL & Redis
   - Deploy!

4. **Your app will be available at**:
   - Frontend: `https://your-app.onrender.com`
   - Backend API: `https://your-app.onrender.com/api/v1/...`
   - API Docs: `https://your-app.onrender.com/docs`

---

## Option 2: Separate Frontend & Backend Services

**Deploy frontend and backend as two separate services.**

### Pros:
- ✅ Scale independently
- ✅ Can use specialized platforms (Vercel for frontend, Render for backend)
- ✅ Better for large teams

### Cons:
- ❌ More complex setup
- ❌ CORS configuration required
- ❌ Two deployments to manage
- ❌ More expensive (two services)

### How to Deploy:

#### Backend on Render:
1. Use existing `Dockerfile` (backend only)
2. Deploy on Render
3. Get backend URL: `https://your-backend.onrender.com`

#### Frontend on Vercel/Netlify (Free):
1. Connect GitHub repo
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api/v1
   ```
5. Deploy!

#### Update CORS on Backend:
```python
# In app/core/config.py
CORS_ORIGINS = ["https://your-frontend.vercel.app"]
```

---

## Option 3: Frontend on CDN + Backend on Render

**Use specialized platforms for each service.**

### Frontend Options (Free Tier):
- **Vercel**: Best for React, auto-deploy from GitHub
- **Netlify**: Similar to Vercel, great for static sites
- **Cloudflare Pages**: Fast, global CDN

### Backend:
- **Render**: PostgreSQL + Redis + Docker support

---

## 💰 Cost Comparison

| Option | Frontend | Backend | Database | Total/Month |
|--------|----------|---------|----------|-------------|
| **Option 1** (Full-Stack) | Included | Free tier or $7 | $7 (Postgres) | **$7-14** |
| **Option 2** (Separate) | Free (Vercel) | $7 (Render) | $7 (Postgres) | **$14** |
| **Option 3** (CDN + Render) | Free | $7 (Render) | $7 (Postgres) | **$14** |

---

## 🎯 My Recommendation

**Use Option 1 (Full-Stack Docker)** because:
1. ✅ Simplest setup
2. ✅ Cheapest ($7/month)
3. ✅ No CORS issues
4. ✅ Single deployment
5. ✅ Your app is not huge, doesn't need separate scaling

---

## 🚀 Quick Start (Option 1)

```bash
# 1. Switch to full-stack Dockerfile
mv Dockerfile Dockerfile.backend-only
mv Dockerfile.fullstack Dockerfile

# 2. Commit changes
git add .
git commit -m "Enable full-stack deployment"
git push origin main

# 3. Deploy on Render (follow RENDER_DEPLOYMENT_GUIDE.md)
```

---

## 📝 Frontend Build Check

Verify your frontend builds correctly:

```bash
cd frontend
npm install
npm run build
# Check that dist/ folder is created with index.html
```

---

## 🔧 Environment Variables Needed

### For Full-Stack Deployment:
```bash
# Backend
SECRET_KEY=<generate>
JWT_SECRET_KEY=<generate>
DATABASE_URL=<render provides>
REDIS_URL=<render provides>
ENVIRONMENT=production
DEBUG=False

# Frontend (built into static files, no runtime env vars needed)
# API calls go to same domain (no CORS)
```

### For Separate Deployment:
```bash
# Backend
SECRET_KEY=<generate>
JWT_SECRET_KEY=<generate>
DATABASE_URL=<render provides>
REDIS_URL=<render provides>
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
DEBUG=False

# Frontend (Vercel/Netlify)
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

---

## ✅ Deployment Checklist

- [ ] Choose deployment option (Option 1 recommended)
- [ ] Update Dockerfile if using Option 1
- [ ] Build frontend locally to test (`npm run build`)
- [ ] Commit and push changes
- [ ] Deploy on Render
- [ ] Add PostgreSQL database
- [ ] Add Redis cache
- [ ] Set environment variables
- [ ] Run database migrations
- [ ] Import quiz questions
- [ ] Test frontend at `https://your-app.onrender.com`
- [ ] Test API at `https://your-app.onrender.com/docs`

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Full Guide**: See `RENDER_DEPLOYMENT_GUIDE.md`
- **Railway Alternative**: See `RAILWAY_DEPLOYMENT_GUIDE.md`

---

**Ready to deploy? Use Option 1 for the easiest path! 🚀**
