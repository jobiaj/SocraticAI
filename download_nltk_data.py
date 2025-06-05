#!/usr/bin/env python3
"""
Download all required NLTK data for the Socrates AI application
"""

import nltk
import sys

def download_nltk_resources():
    """Download all required NLTK resources"""
    resources = [
        'punkt',
        'punkt_tab',
        'wordnet',
        'stopwords',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng'
    ]
    
    print("Downloading NLTK resources...")
    
    for resource in resources:
        try:
            print(f"Downloading {resource}...", end=' ')
            nltk.download(resource, quiet=True)
            print("✓")
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    print("\nDone! All NLTK resources have been downloaded.")

if __name__ == "__main__":
    download_nltk_resources()