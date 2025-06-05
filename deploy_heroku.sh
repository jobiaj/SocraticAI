#!/bin/bash

# Heroku Deployment Script for Socrates AI with Google Gemini
# This script automates the deployment process to Heroku

set -e  # Exit on error

echo "🚀 Socrates AI - Heroku Deployment Script"
echo "========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI is not installed!"
    echo "Please install it from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    print_warning "You're not logged in to Heroku. Logging in..."
    heroku login
fi

# Get app name from user
echo ""
read -p "Enter your Heroku app name (leave blank to create new): " APP_NAME

# Create new app or use existing
if [ -z "$APP_NAME" ]; then
    print_status "Creating new Heroku app..."
    APP_NAME=$(heroku create --json | grep -o '"name":"[^"]*' | grep -o '[^"]*$')
    print_status "Created app: $APP_NAME"
else
    # Check if app exists
    if heroku apps:info -a "$APP_NAME" &> /dev/null; then
        print_status "Using existing app: $APP_NAME"
    else
        print_status "Creating app: $APP_NAME"
        heroku create "$APP_NAME"
    fi
fi

# Set Git remote
print_status "Setting up Git remote..."
heroku git:remote -a "$APP_NAME" 2>/dev/null || true

# Get Google API key
echo ""
echo "Google Gemini API Configuration"
echo "------------------------------"
read -p "Enter your Google API key: " GOOGLE_API_KEY

if [ -z "$GOOGLE_API_KEY" ]; then
    print_error "Google API key is required!"
    exit 1
fi

# Ask for model preference
echo ""
echo "Available Gemini models:"
echo "1. gemini-1.5-flash (recommended - fast and stable)"
echo "2. gemini-2.5-pro-preview-05-06 (more capable but slower)"
echo "3. gemini-pro (legacy model)"
echo "4. Custom model name"
read -p "Select model (1-4) [1]: " MODEL_CHOICE

case $MODEL_CHOICE in
    2)
        GOOGLE_MODEL="gemini-2.5-pro-preview-05-06"
        ;;
    3)
        GOOGLE_MODEL="gemini-pro"
        ;;
    4)
        read -p "Enter custom model name: " GOOGLE_MODEL
        ;;
    *)
        GOOGLE_MODEL="gemini-1.5-flash"
        ;;
esac

print_status "Selected model: $GOOGLE_MODEL"

# Set environment variables
print_status "Setting environment variables..."
heroku config:set LLM_PROVIDER=google -a "$APP_NAME"
heroku config:set GOOGLE_API_KEY="$GOOGLE_API_KEY" -a "$APP_NAME"
heroku config:set GOOGLE_MODEL="$GOOGLE_MODEL" -a "$APP_NAME"

# Set Python runtime
print_status "Setting Python runtime..."
heroku config:set PYTHON_VERSION=3.11.0 -a "$APP_NAME"

# Add buildpacks
print_status "Adding buildpacks..."
heroku buildpacks:add heroku/python -a "$APP_NAME" 2>/dev/null || true

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    print_status "Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv/

# Environment
.env
.env.local
.env.*.local

# NLTK data (will be downloaded during deployment)
nltk_data/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/
EOF
fi

# Initialize git if needed
if [ ! -d .git ]; then
    print_status "Initializing Git repository..."
    git init
    git branch -M main
    git add .
    git commit -m "Initial commit for Socrates AI"
else
    # Check if we have any commits
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
        print_status "No commits found, creating initial commit..."
        git add .
        git commit -m "Initial commit for Socrates AI"
    fi
    
    # Check if we're on main branch, if not create it
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_status "Creating main branch..."
        git checkout -b main 2>/dev/null || git branch -M main
    fi
fi

# Make sure we have recent changes committed
if git diff --quiet && git diff --cached --quiet; then
    print_status "Working directory clean, ready to deploy"
else
    print_status "Committing recent changes..."
    git add .
    git commit -m "Pre-deployment commit $(date)"
fi

# Deploy to Heroku
echo ""
print_status "Starting deployment to Heroku..."
echo "This may take a few minutes..."

# Ensure we're pushing from main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_status "Current branch: $CURRENT_BRANCH"

# Push to Heroku
print_status "Pushing to Heroku..."
if git push heroku main; then
    print_status "Deployment successful!"
elif [ "$CURRENT_BRANCH" = "master" ] && git push heroku master:main; then
    print_status "Deployment successful!"
elif git push heroku "$CURRENT_BRANCH:main"; then
    print_status "Deployment successful!"
else
    print_error "Deployment failed! Please check the error messages above."
    echo ""
    echo "Common solutions:"
    echo "1. Make sure you have commits: git add . && git commit -m 'Deploy'"
    echo "2. Check Heroku remote: git remote -v"
    echo "3. Try manual push: git push heroku main --force"
    exit 1
fi

# Scale the app
print_status "Scaling app to 1 web dyno..."
heroku ps:scale web=1 -a "$APP_NAME"

# Run post-deployment tasks
print_status "Running post-deployment tasks..."
heroku run python download_nltk_data.py -a "$APP_NAME"

# Show app info
echo ""
echo "========================================="
print_status "Deployment Complete! 🎉"
echo ""
echo "App URL: https://$APP_NAME.herokuapp.com"
echo ""
echo "Useful commands:"
echo "- View logs: heroku logs --tail -a $APP_NAME"
echo "- Open app: heroku open -a $APP_NAME"
echo "- Check status: heroku ps -a $APP_NAME"
echo "- Update config: heroku config:set KEY=value -a $APP_NAME"
echo ""

# Ask if user wants to open the app
read -p "Would you like to open the app now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    heroku open -a "$APP_NAME"
fi