# Socrates AI - Philosophical Dialogue Application

An AI-powered web application that engages users in Socratic dialogue using advanced LLM APIs (Claude 4, GPT-4). The application processes user input with NLP techniques and generates thoughtful, philosophical responses.

## Features

- **Socratic Method Implementation**: Engages users through thoughtful questions and philosophical dialogue
- **Multiple LLM Support**: Works with Anthropic Claude, OpenAI GPT, or Google Gemini models
- **NLP Processing**: Tokenization, lemmatization, and POS tagging of user input
- **Web Interface**: Clean, responsive UI for dialogue interaction
- **Error Handling**: Robust handling of API rate limits and errors
- **Input Analysis**: Shows processed NLP data for transparency

## Installation

### Quick Setup (Using Make)

```bash
git clone <repository-url>
cd socrates-app
make setup  # Installs dependencies and downloads NLTK data
# Edit .env file with your API keys
make run    # Start the application
```

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd socrates-app
```

2. Create a virtual environment:
```bash
python -m venv venv # use python or python3 based on your system.
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your API key for either Anthropic, OpenAI, or Google.

5. Download NLTK data:
```bash
python download_nltk_data.py  # use python or python3 based on your system
# OR manually:
python -c "import nltk; nltk.download(['punkt', 'punkt_tab', 'wordnet', 'stopwords', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng'])"
```

## Running the Application

### Local Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` in your browser.

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## API Endpoints

- `GET /` - Web interface
- `POST /api/dialogue` - JSON API endpoint
- `POST /dialogue` - Form submission endpoint
- `GET /health` - Health check endpoint

### API Usage Example

```bash
curl -X POST "http://localhost:8000/api/dialogue" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the nature of truth?"}'
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Create `vercel.json` in the project root:
```json
{
  "builds": [
    {"src": "app/main.py", "use": "@vercel/python"}
  ],
  "routes": [
    {"src": "/(.*)", "dest": "app/main.py"}
  ]
}
```

3. Deploy:
```bash
vercel
```

### Heroku Deployment

**Quick Deployment (Recommended):**
```bash
./deploy_heroku.sh
```

**Manual Deployment:**
See the complete guide: [DEPLOY_HEROKU.md](DEPLOY_HEROKU.md)

**Quick Manual Steps:**
```bash
heroku create your-app-name
heroku config:set LLM_PROVIDER=google
heroku config:set GOOGLE_API_KEY=your-google-key-here
heroku config:set GOOGLE_MODEL=gemini-1.5-flash
git push heroku main
heroku run python download_nltk_data.py
```

### Docker Deployment

Create a `Dockerfile` in the project root:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "import nltk; nltk.download(['punkt', 'wordnet', 'stopwords', 'averaged_perceptron_tagger'])"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t socrates-ai .
docker run -p 8000:8000 --env-file .env socrates-ai
```

## Configuration

### Environment Variables

- `LLM_PROVIDER`: Choose between 'anthropic', 'openai', or 'google'
- `ANTHROPIC_API_KEY`: Your Anthropic API key (if using Claude)
- `ANTHROPIC_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `OPENAI_API_KEY`: Your OpenAI API key (if using GPT)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo-preview)
- `GOOGLE_API_KEY`: Your Google API key (if using Gemini)
- `GOOGLE_MODEL`: Google model to use (recommended: gemini-1.5-flash, gemini-1.5-pro, or gemini-pro)

## Machine Learning Model Training

The application includes a philosophical question categorizer that uses machine learning to classify user questions into different philosophical domains (Ethics, Metaphysics, Epistemology, etc.).

### When to Train the Model

The model training should be executed in the following scenarios:

1. **Initial Setup**: When first setting up the application, if the model files don't exist in the `models/` directory
2. **Model Updates**: When you want to improve the categorization by updating the training data or algorithm
3. **After Major Changes**: After modifying the philosophical categories or training examples in `app/ml_categorizer.py`

### Training the Model

To train or retrain the categorizer model:

```bash
python train_categorizer.py
```

This command will:
- Generate training data from philosophical examples
- Train a Decision Tree classifier
- Save the model files to the `models/` directory:
  - `models/philosophy_categorizer.pkl` - The trained classifier
  - `models/tfidf_vectorizer.pkl` - The text vectorizer
- Display test predictions to verify the model is working

### Automatic Model Loading

When the application starts:
- It automatically attempts to load the pre-trained model from the `models/` directory
- If the model files are not found, it will automatically train a new model
- This ensures the app always has a working categorizer, even on first run

**Note**: The pre-trained model files are included in the repository, so manual training is typically not required unless you want to update or improve the model.

## Project Structure

```
socrates-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── llm_service.py       # LLM API integration
│   ├── nlp_processor.py     # NLP processing logic
│   ├── socratic_dialogue.py # Socratic method implementation
│   └── ml_categorizer.py    # ML categorizer for philosophical questions
├── models/
│   ├── philosophy_categorizer.pkl  # Trained ML model
│   └── tfidf_vectorizer.pkl       # Text vectorizer
├── static/
│   ├── style.css           # CSS styles
│   └── script.js           # Frontend JavaScript
├── templates/
│   └── index.html          # HTML template
├── train_categorizer.py    # Script to train the ML model
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Error Handling

The application handles:
- API rate limits with exponential backoff
- API errors with retries
- Invalid input validation
- Missing API keys
- Network timeouts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### NLTK Data Errors

If you encounter errors like `Resource punkt_tab not found` or `Resource averaged_perceptron_tagger_eng not found`, run:

```bash
python download_nltk_data.py
```

Or manually download all required NLTK data:

```bash
python -c "import nltk; nltk.download('all')"
```

### API Key Issues

Make sure your `.env` file contains the correct API key for your chosen provider:
- For Anthropic: `ANTHROPIC_API_KEY=your-key-here`
- For OpenAI: `OPENAI_API_KEY=your-key-here`
- For Google: `GOOGLE_API_KEY=your-key-here`

### Port Already in Use

If port 8000 is already in use, you can specify a different port:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Google Gemini Safety Filter Issues

If you encounter errors with Google Gemini like "Invalid operation: The response.text quick accessor requires the response to contain a valid Part", this usually means the content was blocked by safety filters. The app now handles this gracefully, but you can:

1. Try rephrasing your question
2. Use a different model like `gemini-1.5-flash` or `gemini-1.5-pro`
3. Switch to a different LLM provider (Anthropic or OpenAI)

Application is deployed here: https://socrates-ai-app-1711abfba870.herokuapp.com/