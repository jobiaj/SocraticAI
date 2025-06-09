#!/usr/bin/env python3
"""
Script to train the philosophical categorizer model.
Run this script to create or update the ML model.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml_categorizer import PhilosophicalCategorizer

def main():
    print("=" * 60)
    print("Philosophical Categorizer Training Script")
    print("=" * 60)
    
    # Create categorizer instance
    categorizer = PhilosophicalCategorizer()
    
    # Train the model
    print("\nTraining the decision tree model...")
    categorizer.train()
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    
    # Test the model with some examples
    print("\nTesting the trained model with sample questions:")
    print("-" * 60)
    
    test_questions = [
        "What is the meaning of life?",
        "Is it ethical to lie to protect someone's feelings?",
        "How do we know what is real?",
        "What makes something beautiful?",
        "Can artificial intelligence be conscious?",
        "What is justice in society?",
        "Does God exist?",
        "What is the nature of truth?",
        "Should we always follow the law?",
        "What is the purpose of art?"
    ]
    
    for question in test_questions:
        try:
            category, scores = categorizer.predict(question)
            print(f"\nQ: {question}")
            print(f"Category: {category}")
            print(f"Description: {categorizer.get_category_description(category)}")
        except Exception as e:
            print(f"Error categorizing '{question}': {e}")
    
    print("\n" + "=" * 60)
    print("Model is ready for use!")
    print("The model files are saved in the 'models' directory.")
    print("=" * 60)

if __name__ == "__main__":
    main()