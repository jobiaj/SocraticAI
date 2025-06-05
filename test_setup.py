#!/usr/bin/env python3
"""
Test script to verify the Socrates AI setup
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
        
        import anthropic
        print("✓ Anthropic imported successfully")
        
        import openai
        print("✓ OpenAI imported successfully")
        
        import google.generativeai
        print("✓ Google GenerativeAI imported successfully")
        
        import nltk
        print("✓ NLTK imported successfully")
        
        from app.main import app
        print("✓ App main imported successfully")
        
        from app.llm_service import LLMService
        print("✓ LLM Service imported successfully")
        
        from app.nlp_processor import NLPProcessor
        print("✓ NLP Processor imported successfully")
        
        from app.socratic_dialogue import SocraticDialogue
        print("✓ Socratic Dialogue imported successfully")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True

def test_env_vars():
    """Test environment variables"""
    print("\nTesting environment variables...")
    load_dotenv()
    
    provider = os.getenv('LLM_PROVIDER')
    if provider:
        print(f"✓ LLM_PROVIDER is set to: {provider}")
        
        if provider == 'anthropic':
            if os.getenv('ANTHROPIC_API_KEY'):
                print("✓ ANTHROPIC_API_KEY is set")
            else:
                print("✗ ANTHROPIC_API_KEY is not set")
                
        elif provider == 'openai':
            if os.getenv('OPENAI_API_KEY'):
                print("✓ OPENAI_API_KEY is set")
            else:
                print("✗ OPENAI_API_KEY is not set")
                
        elif provider == 'google':
            if os.getenv('GOOGLE_API_KEY'):
                print("✓ GOOGLE_API_KEY is set")
            else:
                print("✗ GOOGLE_API_KEY is not set")
    else:
        print("✗ LLM_PROVIDER is not set")

def test_nltk_data():
    """Test NLTK data availability"""
    print("\nTesting NLTK data...")
    import nltk
    
    required_data = [
        ('tokenizers/punkt', 'punkt'),
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/wordnet', 'wordnet'),
        ('corpora/stopwords', 'stopwords'),
        ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
        ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng')
    ]
    
    for path, name in required_data:
        try:
            nltk.data.find(path)
            print(f"✓ NLTK {name} data found")
        except LookupError:
            print(f"✗ NLTK {name} data not found - run: python -c \"import nltk; nltk.download('{name}')\"")

def main():
    print("=== Socrates AI Setup Test ===\n")
    
    # Test imports
    if not test_imports():
        print("\nSome imports failed. Please check your installation.")
        sys.exit(1)
    
    # Test environment variables
    test_env_vars()
    
    # Test NLTK data
    test_nltk_data()
    
    print("\n=== Test Complete ===")
    print("\nTo run the application:")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()