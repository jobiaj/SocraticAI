# Heroku Deployment Guide for Socrates AI

This guide walks you through deploying Socrates AI to Heroku with Google Gemini as the LLM provider.

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Ensure Git is installed on your system
4. **Google API Key**: Get one from [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

## Quick Deployment (Automated)

Use the provided deployment script for the easiest setup:

```bash
./deploy_heroku.sh
```

The script will:
- Check prerequisites
- Create or connect to a Heroku app
- Configure Google Gemini as the LLM provider
- Deploy the application
- Set up NLTK data

## Manual Deployment Steps

If you prefer to deploy manually or the script doesn't work:

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create a Heroku App

```bash
# Create app with a specific name
heroku create your-app-name

# Or create with auto-generated name
heroku create
```

### 3. Set Environment Variables

```bash
# Set LLM provider to Google
heroku config:set LLM_PROVIDER=google

# Set your Google API key
heroku config:set GOOGLE_API_KEY="your-google-api-key-here"

# Set the Gemini model (recommended: gemini-1.5-flash)
heroku config:set GOOGLE_MODEL="gemini-1.5-flash"
```

### 4. Initialize Git (if needed)

```bash
git init
git add .
git commit -m "Initial commit"
```

### 5. Add Heroku Remote

```bash
heroku git:remote -a your-app-name
```

### 6. Deploy to Heroku

```bash
git push heroku main

# If your branch is named 'master':
git push heroku master

# If using a different branch:
git push heroku your-branch:main
```

### 7. Scale the Application

```bash
heroku ps:scale web=1
```

### 8. Download NLTK Data

```bash
heroku run python download_nltk_data.py
```

### 9. Open Your App

```bash
heroku open
```

## Configuration Options

### Google Gemini Models

You can use any of these models by setting `GOOGLE_MODEL`:

- `gemini-1.5-flash` - Fast and reliable (recommended)
- `gemini-1.5-pro` - More capable but slower
- `gemini-2.0-flash-exp` - Experimental, fast model
- `gemini-pro` - Legacy model

Example:
```bash
heroku config:set GOOGLE_MODEL="gemini-1.5-pro"
```

### Switching LLM Providers

To switch to a different LLM provider:

**For OpenAI:**
```bash
heroku config:set LLM_PROVIDER=openai
heroku config:set OPENAI_API_KEY="your-openai-key"
heroku config:set OPENAI_MODEL="gpt-4-turbo-preview"
```

**For Anthropic:**
```bash
heroku config:set LLM_PROVIDER=anthropic
heroku config:set ANTHROPIC_API_KEY="your-anthropic-key"
heroku config:set ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

## Monitoring and Logs

### View Real-time Logs
```bash
heroku logs --tail
```

### Check App Status
```bash
heroku ps
```

### View Configuration
```bash
heroku config
```

## Troubleshooting

### 1. Application Error on First Load

This might happen if NLTK data hasn't downloaded. Run:
```bash
heroku run python download_nltk_data.py
heroku restart
```

### 2. Google API Errors

If you see "Invalid operation" or safety filter errors:
- Try using `gemini-1.5-flash` model
- Ensure your API key is valid
- Check if the API is enabled in Google Cloud Console

### 3. Memory Issues

If you encounter R14 (Memory quota exceeded) errors:
- The free Heroku dyno has 512MB RAM limit
- Consider upgrading to a paid dyno

### 4. Build Failures

If deployment fails:
- Check that `runtime.txt` specifies `python-3.11.0`
- Ensure all dependencies are in `requirements.txt`
- Check build logs: `heroku logs --tail`

## Updating Your App

To deploy updates:

```bash
git add .
git commit -m "Update description"
git push heroku main
```

## Useful Heroku Commands

```bash
# Restart app
heroku restart

# Run Python shell
heroku run python

# Run any command
heroku run bash

# Check dyno usage
heroku ps:type

# View all config vars
heroku config

# Remove the app
heroku apps:destroy --confirm your-app-name
```

## Cost Considerations

- **Free Tier**: 550-1000 dyno hours/month (with verification)
- **Basic Tier**: $7/month for always-on
- **Google API**: Free tier includes $300 credit
- **Bandwidth**: 2TB free on Heroku

## Security Best Practices

1. Never commit API keys to Git
2. Use Heroku config vars for all secrets
3. Regularly rotate API keys
4. Monitor usage and logs for anomalies

## Support

If you encounter issues:
1. Check Heroku status: [status.heroku.com](https://status.heroku.com)
2. Review logs: `heroku logs --tail`
3. Check the [troubleshooting section](#troubleshooting)
4. Open an issue on the project repository