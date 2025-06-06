#!/bin/bash

# Heroku Redeploy Script - Switch from Google to OpenAI
# This script stops the current app and reconfigures it for OpenAI GPT

set -e  # Exit on error

echo "🔄 Socrates AI - Switch to OpenAI & Redeploy"
echo "============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
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

# Get app name from user or try to detect it
echo ""
if git remote get-url heroku &> /dev/null; then
    HEROKU_URL=$(git remote get-url heroku)
    APP_NAME=$(echo "$HEROKU_URL" | sed 's/.*heroku\.com[:/]\([^./]*\)\.git.*/\1/')
    print_info "Detected Heroku app: $APP_NAME"
    read -p "Is this correct? (y/n) [y]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        read -p "Enter your Heroku app name: " APP_NAME
    fi
else
    read -p "Enter your Heroku app name: " APP_NAME
fi

if [ -z "$APP_NAME" ]; then
    print_error "App name is required!"
    exit 1
fi

# Verify app exists
if ! heroku apps:info -a "$APP_NAME" &> /dev/null; then
    print_error "App '$APP_NAME' not found or you don't have access to it!"
    echo "Available apps:"
    heroku apps --json | grep -o '"name":"[^"]*' | cut -d'"' -f4
    exit 1
fi

print_status "Using Heroku app: $APP_NAME"

# Show current configuration
echo ""
print_info "Current app configuration:"
heroku config -a "$APP_NAME" | grep -E "(LLM_PROVIDER|ANTHROPIC|OPENAI|GOOGLE)" || echo "No LLM config found"

# Stop the application
echo ""
print_status "Stopping application..."
heroku ps:scale web=0 -a "$APP_NAME"

# Get OpenAI API key
echo ""
echo "OpenAI API Configuration"
echo "------------------------"
echo "Get your API key from: https://platform.openai.com/api-keys"
echo ""

# Check if OpenAI key is already set
EXISTING_OPENAI_KEY=$(heroku config:get OPENAI_API_KEY -a "$APP_NAME" 2>/dev/null || echo "")
if [ -n "$EXISTING_OPENAI_KEY" ] && [ "$EXISTING_OPENAI_KEY" != "your-openai-api-key-here" ]; then
    print_info "OpenAI API key is already configured"
    read -p "Do you want to use the existing key? (y/n) [y]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        OPENAI_API_KEY="$EXISTING_OPENAI_KEY"
    fi
fi

if [ -z "$OPENAI_API_KEY" ]; then
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OpenAI API key is required!"
        exit 1
    fi
fi

# Ask for model preference
echo ""
echo "Available OpenAI models:"
echo "1. gpt-4o (latest GPT-4 model - recommended)"
echo "2. gpt-4-turbo (fast and capable)"
echo "3. gpt-4 (standard GPT-4)"
echo "4. gpt-3.5-turbo (faster, less capable)"
echo "5. Custom model name"
read -p "Select model (1-5) [1]: " MODEL_CHOICE

case $MODEL_CHOICE in
    2)
        OPENAI_MODEL="gpt-4-turbo"
        ;;
    3)
        OPENAI_MODEL="gpt-4"
        ;;
    4)
        OPENAI_MODEL="gpt-3.5-turbo"
        ;;
    5)
        read -p "Enter custom model name: " OPENAI_MODEL
        ;;
    *)
        OPENAI_MODEL="gpt-4o"
        ;;
esac

print_status "Selected model: $OPENAI_MODEL"

# Remove old LLM provider configs
echo ""
print_status "Removing old LLM provider configurations..."
heroku config:unset GOOGLE_API_KEY GOOGLE_MODEL ANTHROPIC_API_KEY ANTHROPIC_MODEL -a "$APP_NAME" 2>/dev/null || true

# Set new environment variables
print_status "Setting OpenAI configuration..."
heroku config:set LLM_PROVIDER=openai -a "$APP_NAME"
heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" -a "$APP_NAME"
heroku config:set OPENAI_MODEL="$OPENAI_MODEL" -a "$APP_NAME"

# Test the API key locally if possible
print_status "Testing OpenAI API key..."
if command -v python3 &> /dev/null && python3 -c "import openai" 2>/dev/null; then
    export OPENAI_API_KEY="$OPENAI_API_KEY"
    export OPENAI_MODEL="$OPENAI_MODEL"
    
    if python3 -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL'),
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    print('✓ API key is valid!')
except Exception as e:
    print(f'✗ API test failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_status "OpenAI API key is valid!"
    else
        print_warning "Could not validate API key locally (will be tested during deployment)"
    fi
else
    print_warning "Could not test API key locally (OpenAI package not available)"
fi

# Ask about deployment
echo ""
read -p "Do you want to deploy the application now? (y/n) [y]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_info "Configuration updated. To deploy later, run:"
    echo "  git push heroku main"
    echo "  heroku ps:scale web=1 -a $APP_NAME"
    exit 0
fi

# Make sure we have recent changes committed
if git diff --quiet && git diff --cached --quiet; then
    print_status "Working directory clean, ready to deploy"
else
    print_status "Committing recent changes..."
    git add .
    git commit -m "Switch to OpenAI provider - $(date)"
fi

# Deploy to Heroku
echo ""
print_status "Starting deployment to Heroku..."
echo "This may take a few minutes..."

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
print_info "Deploying from branch: $CURRENT_BRANCH"

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
    echo "You can try:"
    echo "1. Manual push: git push heroku main"
    echo "2. Force push: git push heroku main --force"
    echo "3. Check logs: heroku logs --tail -a $APP_NAME"
    exit 1
fi

# Scale the app back up
print_status "Starting application (scaling to 1 web dyno)..."
heroku ps:scale web=1 -a "$APP_NAME"

# Wait a moment for app to start
echo ""
print_info "Waiting for app to start..."
sleep 10

# Check app status
print_status "Checking app status..."
heroku ps -a "$APP_NAME"

# Show logs to verify startup
echo ""
print_info "Recent logs:"
heroku logs --tail --num 20 -a "$APP_NAME" &
LOGS_PID=$!

# Wait a few seconds then kill log tail
sleep 15
kill $LOGS_PID 2>/dev/null || true

# Show app info
echo ""
echo "========================================="
print_status "Redeployment Complete! 🎉"
echo ""
echo "App URL: https://$APP_NAME.herokuapp.com"
echo "LLM Provider: OpenAI ($OPENAI_MODEL)"
echo ""
echo "Useful commands:"
echo "- View logs: heroku logs --tail -a $APP_NAME"
echo "- Open app: heroku open -a $APP_NAME"
echo "- Check status: heroku ps -a $APP_NAME"
echo "- View config: heroku config -a $APP_NAME"
echo ""

# Ask if user wants to open the app
read -p "Would you like to open the app now? (y/n) [y]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    heroku open -a "$APP_NAME"
fi

echo ""
print_status "Redeploy complete! Your app is now using OpenAI GPT."