# Philosophical Question Categorizer

## Overview

The Socrates AI app now includes a machine learning component that automatically categorizes user questions into philosophical domains using a Decision Tree classifier.

## Features

- **Automatic Classification**: Categorizes questions into 10 philosophical categories
- **Decision Tree Model**: Uses scikit-learn's DecisionTreeClassifier for interpretable predictions
- **TF-IDF Features**: Leverages text frequency analysis for better understanding
- **Keyword Detection**: Identifies philosophical keywords for enhanced accuracy

## Categories

The model classifies questions into these philosophical domains:

1. **Ethics** - Moral philosophy, right/wrong, values
2. **Metaphysics** - Reality, existence, being, time, space
3. **Epistemology** - Knowledge, truth, belief, certainty
4. **Logic** - Reasoning, arguments, validity
5. **Aesthetics** - Beauty, art, taste, creativity
6. **Political** - Justice, society, government, rights
7. **Mind** - Consciousness, thought, mental phenomena
8. **Language** - Meaning, communication, semantics
9. **Religion** - God, faith, spirituality
10. **General** - Broad philosophical inquiries

## Training the Model

To train or retrain the categorizer:

```bash
python train_categorizer.py
```

This will:
- Create training data from philosophical examples
- Train the Decision Tree model
- Save the model to `models/` directory
- Display accuracy metrics and test predictions

## Integration

The categorizer is automatically integrated into the main app:
- Loads pre-trained model on startup
- Categorizes each user input
- Displays category in the web interface
- Passes category info to Socratic dialogue system

## Model Architecture

- **Preprocessing**: Lowercase, punctuation removal, whitespace normalization
- **Feature Extraction**: 
  - TF-IDF vectorization (max 100 features, 1-2 grams)
  - Philosophical keyword detection
- **Classifier**: Decision Tree with max depth of 10

## Performance

The model achieves good accuracy on the training set. For production use, consider:
- Expanding training data
- Cross-validation for better generalization
- Ensemble methods for improved accuracy
- Regular retraining with user feedback

## Files

- `app/ml_categorizer.py` - Main categorizer module
- `train_categorizer.py` - Training script
- `models/philosophy_categorizer.pkl` - Trained model (generated)
- `models/tfidf_vectorizer.pkl` - Fitted vectorizer (generated)