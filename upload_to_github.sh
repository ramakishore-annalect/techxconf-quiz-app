#!/bin/bash

# GitHub Upload Script for OGS TechXConf Quiz App
# This script helps you upload your project to GitHub

set -e  # Exit on error

echo "================================================"
echo "🚀 GitHub Upload Helper Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install Git first.${NC}"
    echo "Install from: https://git-scm.com/download/mac"
    exit 1
fi

echo -e "${GREEN}✅ Git is installed${NC}"
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}❌ GitHub username cannot be empty${NC}"
    exit 1
fi

# Get repository name
read -p "Enter repository name (default: techxconf-quiz-app): " REPO_NAME
REPO_NAME=${REPO_NAME:-techxconf-quiz-app}

echo ""
echo "================================================"
echo "📋 Configuration"
echo "================================================"
echo "GitHub Username: $GITHUB_USERNAME"
echo "Repository Name: $REPO_NAME"
echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo ""

read -p "Is this correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo -e "${YELLOW}⚠️  Cancelled by user${NC}"
    exit 0
fi

echo ""
echo "================================================"
echo "🔍 Checking for sensitive files..."
echo "================================================"

# Check for .env files
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Found .env file (will be ignored by .gitignore)${NC}"
fi

if [ -f "frontend/.env" ]; then
    echo -e "${YELLOW}⚠️  Found frontend/.env file (will be ignored by .gitignore)${NC}"
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}❌ .gitignore file not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .gitignore file exists${NC}"
echo ""

echo "================================================"
echo "📝 Checking README..."
echo "================================================"

# Use the GitHub README if it exists
if [ -f "README_GITHUB.md" ]; then
    echo -e "${YELLOW}📄 Replacing README.md with README_GITHUB.md${NC}"
    cp README_GITHUB.md README.md
    echo -e "${GREEN}✅ README.md updated${NC}"
else
    echo -e "${YELLOW}⚠️  README_GITHUB.md not found, using existing README.md${NC}"
fi

echo ""
echo "================================================"
echo "🎯 Initializing Git Repository..."
echo "================================================"

# Check if git is already initialized
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository already initialized${NC}"
    read -p "Reinitialize? This will remove existing git history. (y/n): " REINIT
    if [ "$REINIT" == "y" ]; then
        rm -rf .git
        git init
        echo -e "${GREEN}✅ Git repository reinitialized${NC}"
    fi
else
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi

echo ""
echo "================================================"
echo "➕ Adding files to git..."
echo "================================================"

git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -20
echo ""

# Count files
FILE_COUNT=$(git status --short | wc -l)
echo -e "${GREEN}✅ $FILE_COUNT files staged${NC}"

echo ""
echo "================================================"
echo "💾 Creating initial commit..."
echo "================================================"

git commit -m "Initial commit: OGS TechXConf Quiz App

- FastAPI backend with PostgreSQL and Redis
- React/TypeScript frontend with Tailwind CSS
- 428 questions across 9 technical topics
- 15-second per-question timer
- User authentication and leaderboard
- Docker Compose setup for easy deployment
- Comprehensive documentation"

echo -e "${GREEN}✅ Initial commit created${NC}"

echo ""
echo "================================================"
echo "🌐 Adding GitHub remote..."
echo "================================================"

# Check if remote already exists
if git remote | grep -q origin; then
    echo -e "${YELLOW}⚠️  Remote 'origin' already exists${NC}"
    EXISTING_REMOTE=$(git remote get-url origin)
    echo "Existing remote: $EXISTING_REMOTE"
    read -p "Replace with new remote? (y/n): " REPLACE_REMOTE
    if [ "$REPLACE_REMOTE" == "y" ]; then
        git remote remove origin
        git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo -e "${GREEN}✅ Remote replaced${NC}"
    fi
else
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo -e "${GREEN}✅ Remote 'origin' added${NC}"
fi

# Rename branch to main
git branch -M main
echo -e "${GREEN}✅ Branch renamed to 'main'${NC}"

echo ""
echo "================================================"
echo "📤 Ready to push to GitHub!"
echo "================================================"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Before pushing, make sure you:${NC}"
echo "1. Created the repository on GitHub: https://github.com/new"
echo "2. Have a Personal Access Token ready (if using HTTPS)"
echo "   - Create one at: https://github.com/settings/tokens"
echo "   - Select 'repo' scope"
echo "   - Use the token as your password when pushing"
echo ""

read -p "Have you created the repository on GitHub? (y/n): " REPO_CREATED

if [ "$REPO_CREATED" != "y" ]; then
    echo ""
    echo -e "${YELLOW}📌 Please create the repository on GitHub first:${NC}"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Choose Private or Public"
    echo "4. Do NOT initialize with README, .gitignore, or license"
    echo "5. Click 'Create repository'"
    echo ""
    echo "After creating the repository, run:"
    echo -e "${GREEN}git push -u origin main${NC}"
    exit 0
fi

echo ""
read -p "Push to GitHub now? (y/n): " PUSH_NOW

if [ "$PUSH_NOW" == "y" ]; then
    echo ""
    echo "================================================"
    echo "🚀 Pushing to GitHub..."
    echo "================================================"
    echo ""
    echo "If prompted for credentials:"
    echo "- Username: $GITHUB_USERNAME"
    echo "- Password: Use your Personal Access Token (not your GitHub password)"
    echo ""
    
    if git push -u origin main; then
        echo ""
        echo "================================================"
        echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
        echo "================================================"
        echo ""
        echo "Your repository is now available at:"
        echo -e "${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Visit your repository URL"
        echo "2. Verify all files are present"
        echo "3. Check that README.md displays correctly"
        echo "4. Set up branch protection rules (optional)"
        echo "5. Add collaborators (optional)"
        echo ""
    else
        echo ""
        echo "================================================"
        echo -e "${RED}❌ Push failed${NC}"
        echo "================================================"
        echo ""
        echo "Common issues:"
        echo "1. Repository doesn't exist on GitHub"
        echo "2. Authentication failed (need Personal Access Token)"
        echo "3. Network connection issues"
        echo ""
        echo "Try pushing manually:"
        echo -e "${GREEN}git push -u origin main${NC}"
        echo ""
        exit 1
    fi
else
    echo ""
    echo "================================================"
    echo "📋 Manual Push Instructions"
    echo "================================================"
    echo ""
    echo "When you're ready to push, run:"
    echo -e "${GREEN}git push -u origin main${NC}"
    echo ""
    echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
fi

echo "================================================"
echo "🎉 Setup Complete!"
echo "================================================"
