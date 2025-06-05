#!/bin/bash

# Quick fix script for Git deployment issues
# Run this if you encountered the "ambiguous argument 'HEAD'" error

echo "🔧 Fixing Git repository for Heroku deployment..."

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "Initializing Git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "Adding all files..."
git add .

# Create initial commit if none exists
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "Creating initial commit..."
    git commit -m "Initial commit for Socrates AI deployment"
fi

# Ensure we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Switching to main branch..."
    git checkout -b main 2>/dev/null || git branch -M main
fi

# Show git status
echo ""
echo "Git status:"
git status --short

echo ""
echo "✅ Git repository is now ready for deployment!"
echo ""
echo "You can now run:"
echo "  ./deploy_heroku.sh"
echo ""
echo "Or deploy manually with:"
echo "  git push heroku main"