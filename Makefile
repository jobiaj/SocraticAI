.PHONY: install setup run test clean docker-build docker-run deploy-heroku test-google help

# Default Python command
PYTHON := python3

help:
	@echo "Socrates AI - Available commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make setup        - Download NLTK data and set up environment"
	@echo "  make run          - Run the application locally"
	@echo "  make test         - Run the setup test"
	@echo "  make test-google  - Test Google Gemini API connection"
	@echo "  make clean        - Clean up cache files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make deploy-heroku - Deploy to Heroku (interactive)"

install:
	$(PYTHON) -m pip install -r requirements.txt

setup: install
	$(PYTHON) download_nltk_data.py
	@echo "Creating .env file from example..."
	@cp -n .env.example .env || true
	@echo "Setup complete! Edit .env file with your API keys."

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) test_setup.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf nltk_data

docker-build:
	docker build -t socrates-ai .

docker-run:
	docker run -p 8000:8000 --env-file .env socrates-ai

test-google:
	$(PYTHON) test_google_api.py

deploy-heroku:
	./deploy_heroku.sh