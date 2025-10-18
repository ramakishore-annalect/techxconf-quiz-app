# GitHub Upload Guide - OGS TechXConf Quiz App

## 📋 Prerequisites
- GitHub account (create one at [github.com](https://github.com) if you don't have one)
- Git installed on your Mac (check with `git --version`)

---

## 🚀 Step-by-Step Guide

### Step 1: Create a New Repository on GitHub

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in the top-right corner
3. Select **"New repository"**
4. Configure your repository:
   - **Repository name**: `techxconf-quiz-app` (or your preferred name)
   - **Description**: "OGS TechXConf Quiz Application - A full-stack quiz platform with FastAPI backend and React frontend"
   - **Visibility**: 
     - ✅ **Private** (recommended if you want to keep it internal)
     - Or **Public** (if you want to share it)
   - **Do NOT** check "Initialize this repository with a README" (we already have files)
   - **Do NOT** add .gitignore or license (we already have them)
5. Click **"Create repository"**

6. **Copy the repository URL** shown on the next page (it will look like):
   - HTTPS: `https://github.com/YOUR_USERNAME/techxconf-quiz-app.git`
   - SSH: `git@github.com:YOUR_USERNAME/techxconf-quiz-app.git`

---

### Step 2: Prepare Your Local Repository

Open Terminal and run these commands:

```bash
# Navigate to your project directory
cd /Users/ramakishore.nooji/Annalect\ Code/techxconf_quiz_app

# Initialize git repository
git init

# Check git status (see what files will be added)
git status

# Add all files to staging (respects .gitignore)
git add .

# Check what's staged
git status

# Create your first commit
git commit -m "Initial commit: OGS TechXConf Quiz App with 428 questions"
```

---

### Step 3: Connect to GitHub and Push

```bash
# Add your GitHub repository as remote
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/techxconf-quiz-app.git

# Verify the remote was added
git remote -v

# Rename the default branch to 'main' (GitHub standard)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

**Note**: You may be prompted to enter your GitHub credentials:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

---

### Step 4: Create GitHub Personal Access Token (If Needed)

If you don't have a Personal Access Token:

1. Go to GitHub → Click your profile picture → **Settings**
2. Scroll down to **Developer settings** (bottom of left sidebar)
3. Click **Personal access tokens** → **Tokens (classic)**
4. Click **"Generate new token"** → **"Generate new token (classic)"**
5. Configure:
   - **Note**: "TechXConf Quiz App"
   - **Expiration**: 90 days (or your preference)
   - **Select scopes**: Check ✅ **repo** (all sub-options)
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)
8. Use this token as your password when pushing to GitHub

---

### Step 5: Verify Upload

1. Go to your GitHub repository URL in your browser
2. You should see all your project files
3. Check that:
   - ✅ README.md is displayed
   - ✅ All folders are present (app, frontend, scripts, etc.)
   - ✅ Sensitive files are NOT present (.env, __pycache__, etc.)

---

## 📝 Create a Better README (Optional but Recommended)

Create a comprehensive README to showcase your project on GitHub:

```bash
# This will be done in the next step - I'll create an enhanced README for you
```

---

## 🔐 Important: Protect Sensitive Information

Before pushing, ensure these files are NOT being uploaded (they should be in .gitignore):

### Already Protected (in .gitignore):
- ✅ `.env` files (database credentials, secrets)
- ✅ `__pycache__/` (Python cache)
- ✅ `node_modules/` (Node dependencies)
- ✅ `.vscode/` (editor settings)
- ✅ `*.log` (log files)

### Check Your .env Files:
```bash
# Make sure .env files are not tracked
git status | grep .env

# If any .env files appear, add them to .gitignore:
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.production" >> .gitignore
echo "frontend/.env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore to exclude .env files"
```

---

## 🗂️ Recommended .gitignore Additions

Add these to your `.gitignore` to keep your repo clean:

```bash
# Add Excel source files (optional - if you don't want to share question sources)
*.xlsx
*.xls

# Add sensitive configuration
.env*
!.env.example

# Add database files
*.db
*.sqlite
*.sql

# Add Docker volumes
postgres_data/
redis_data/
```

---

## 📦 What Gets Uploaded vs What Stays Local

### ✅ Uploaded to GitHub:
- Source code (Python, TypeScript, React)
- Configuration files (docker-compose.yml, requirements.txt, package.json)
- Documentation (README, deployment guides)
- Database migrations (alembic/versions)
- Scripts (import_xlsx.py, manage.py)
- Frontend assets (public folder, components)

### ❌ NOT Uploaded (Stays Local):
- Environment variables (.env files)
- Database data (postgres data)
- Python cache (__pycache__)
- Node modules (node_modules/)
- Build artifacts (dist/, build/)
- Log files (*.log)
- IDE settings (.vscode/, .idea/)
- Excel source files (*.xlsx) - optional

---

## 🔄 Future Updates - How to Push Changes

After your initial upload, when you make changes:

```bash
# Check what changed
git status

# Add specific files or all changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: improved leaderboard display"

# Push to GitHub
git push origin main
```

### Good Commit Message Examples:
- ✅ `"Fix: Timer bug where questions auto-advance prematurely"`
- ✅ `"Add: 428 new questions across 9 topics"`
- ✅ `"Update: Frontend logo to OGS branding"`
- ✅ `"Refactor: Remove duplicate questions from database"`
- ❌ `"changes"` (too vague)
- ❌ `"fixes"` (not descriptive)

---

## 🌿 GitHub Best Practices

### Create a .env.example File
Help others know what environment variables are needed:

```bash
# Create example env file (without real credentials)
cat > .env.example << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_USER=quiz_user
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=quiz_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Settings
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
ENVIRONMENT=development
DEBUG=True

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
EOF

# Add and commit
git add .env.example
git commit -m "Add .env.example for easy setup"
git push origin main
```

### Add GitHub Actions (CI/CD) - Optional
Create `.github/workflows/tests.yml` for automated testing when you push code.

---

## 📊 Repository Structure on GitHub

Your GitHub repo will look like this:

```
techxconf-quiz-app/
├── 📄 README.md
├── 📄 DEPLOYMENT_GUIDE.md
├── 📄 requirements.txt
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📂 app/
│   ├── 📂 api/
│   ├── 📂 core/
│   ├── 📂 models/
│   ├── 📂 schemas/
│   └── 📂 services/
├── 📂 frontend/
│   ├── 📄 package.json
│   ├── 📂 src/
│   └── 📂 public/
├── 📂 alembic/
├── 📂 scripts/
├── 📂 tests/
└── 📂 monitoring/
```

---

## ✅ Verification Checklist

After pushing to GitHub, verify:

- [ ] Repository is created on GitHub
- [ ] All source code files are visible
- [ ] README.md displays properly on the repo homepage
- [ ] No sensitive files (.env, credentials) are visible
- [ ] File structure matches your local project
- [ ] You can clone the repo to a different location for testing

---

## 🆘 Troubleshooting

### Problem: "Permission denied"
**Solution**: Use HTTPS URL instead of SSH, or set up SSH keys:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/techxconf-quiz-app.git
git push -u origin main
```

### Problem: "Updates were rejected"
**Solution**: Pull first, then push:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### Problem: "Large files detected"
**Solution**: Remove large files from git history:
```bash
# Remove large file from git
git rm --cached path/to/large/file
echo "path/to/large/file" >> .gitignore
git add .gitignore
git commit -m "Remove large file"
git push origin main
```

### Problem: "Username/Password authentication failed"
**Solution**: You need a Personal Access Token (see Step 4)

---

## 🎯 Quick Command Summary

```bash
# One-time setup
git init
git add .
git commit -m "Initial commit: OGS TechXConf Quiz App"
git remote add origin https://github.com/YOUR_USERNAME/techxconf-quiz-app.git
git branch -M main
git push -u origin main

# For future changes
git add .
git commit -m "Your descriptive message"
git push origin main
```

---

## 📞 Need Help?

- **Git Documentation**: [git-scm.com/doc](https://git-scm.com/doc)
- **GitHub Guides**: [guides.github.com](https://guides.github.com)
- **GitHub Support**: [support.github.com](https://support.github.com)

---

**Ready to upload? Follow Step 1 and work your way through! 🚀**
