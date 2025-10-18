#!/bin/bash

# Railway Deployment Quick Start Script
# This script helps you deploy your TechXConf Quiz App to Railway.app

set -e  # Exit on error

echo "🚂 Railway.app Deployment Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
echo "Checking Railway CLI installation..."
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI not found. Installing...${NC}"
    npm i -g @railway/cli
    echo -e "${GREEN}✓ Railway CLI installed successfully${NC}"
else
    echo -e "${GREEN}✓ Railway CLI is already installed${NC}"
fi

echo ""
echo "Step 1: Login to Railway"
echo "------------------------"
railway login
echo -e "${GREEN}✓ Logged in to Railway${NC}"

echo ""
echo "Step 2: Choose Deployment Method"
echo "--------------------------------"
echo "1) Create new project from scratch (CLI method)"
echo "2) I've already created a project on Railway Dashboard"
read -p "Choose option (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo ""
    echo "Creating new Railway project..."
    railway init
    
    echo ""
    echo "Step 3: Add PostgreSQL Database"
    echo "-------------------------------"
    read -p "Do you want to add PostgreSQL? (y/n): " add_pg
    if [ "$add_pg" == "y" ]; then
        railway add --database postgresql
        echo -e "${GREEN}✓ PostgreSQL added${NC}"
    fi
    
    echo ""
    echo "Step 4: Add Redis"
    echo "-----------------"
    read -p "Do you want to add Redis? (y/n): " add_redis
    if [ "$add_redis" == "y" ]; then
        railway add --database redis
        echo -e "${GREEN}✓ Redis added${NC}"
    fi
    
elif [ "$choice" == "2" ]; then
    echo ""
    echo "Linking to existing Railway project..."
    railway link
    echo -e "${GREEN}✓ Linked to Railway project${NC}"
fi

echo ""
echo "Step 5: Configure Environment Variables"
echo "---------------------------------------"
echo "Generating secure secret keys..."

# Generate secret keys
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo ""
echo -e "${BLUE}Generated Secret Keys:${NC}"
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo ""

read -p "Do you want to set these environment variables? (y/n): " set_vars
if [ "$set_vars" == "y" ]; then
    railway variables set SECRET_KEY="$SECRET_KEY"
    railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
    railway variables set ENVIRONMENT="production"
    railway variables set DEBUG="False"
    echo -e "${GREEN}✓ Environment variables set${NC}"
fi

echo ""
echo "Step 6: Deploy to Railway"
echo "-------------------------"
read -p "Ready to deploy? (y/n): " deploy
if [ "$deploy" == "y" ]; then
    echo "Deploying to Railway..."
    railway up
    echo -e "${GREEN}✓ Deployment initiated${NC}"
fi

echo ""
echo "Step 7: Generate Public Domain"
echo "------------------------------"
read -p "Do you want to generate a public domain? (y/n): " gen_domain
if [ "$gen_domain" == "y" ]; then
    railway domain
    echo -e "${GREEN}✓ Domain generated${NC}"
fi

echo ""
echo "Step 8: Run Database Migrations"
echo "-------------------------------"
read -p "Do you want to run database migrations? (y/n): " run_migrations
if [ "$run_migrations" == "y" ]; then
    echo "Running migrations..."
    railway run alembic upgrade head
    echo -e "${GREEN}✓ Migrations completed${NC}"
fi

echo ""
echo "Step 9: Import Quiz Questions (Optional)"
echo "----------------------------------------"
read -p "Do you have Cloud_AI_Quiz_450.xlsx file to import? (y/n): " import_questions
if [ "$import_questions" == "y" ]; then
    if [ -f "Cloud_AI_Quiz_450.xlsx" ]; then
        echo "Importing questions..."
        railway run python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace
        echo -e "${GREEN}✓ Questions imported${NC}"
    else
        echo -e "${RED}✗ Cloud_AI_Quiz_450.xlsx not found in current directory${NC}"
        echo "You can import questions later with:"
        echo "railway run python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx --mode replace"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Railway Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Get your app URL: railway status"
echo "2. View logs: railway logs"
echo "3. Open dashboard: railway open"
echo "4. Test your app at the generated domain"
echo ""
echo "Useful Commands:"
echo "- View status: railway status"
echo "- View logs: railway logs"
echo "- View variables: railway variables"
echo "- Run commands: railway run <command>"
echo "- Open dashboard: railway open"
echo ""
echo -e "${BLUE}Happy deploying! 🚀${NC}"
