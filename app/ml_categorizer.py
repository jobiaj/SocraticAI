import pickle
import os
from typing import List, Tuple, Dict
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import re
import string

class PhilosophicalCategorizer:
    """
    A machine learning categorizer that classifies user questions into philosophical categories
    using a Decision Tree model.
    """
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.categories = [
            'ethics',           # Questions about right/wrong, morality
            'metaphysics',      # Questions about reality, existence, being
            'epistemology',     # Questions about knowledge, truth, belief
            'logic',            # Questions about reasoning, arguments
            'aesthetics',       # Questions about beauty, art, taste
            'political',        # Questions about society, justice, government
            'mind',             # Questions about consciousness, thought
            'language',         # Questions about meaning, communication
            'religion',         # Questions about God, faith, spirituality
            'general'           # General philosophical inquiries
        ]
        self.model_path = 'models/philosophy_categorizer.pkl'
        self.vectorizer_path = 'models/tfidf_vectorizer.pkl'
        
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better feature extraction."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract philosophical keywords from text."""
        keywords = {
            'ethics': ['moral', 'ethics', 'right', 'wrong', 'good', 'evil', 'virtue', 'duty', 'obligation', 'should', 'ought'],
            'metaphysics': ['exist', 'reality', 'being', 'essence', 'substance', 'universe', 'time', 'space', 'cause', 'effect'],
            'epistemology': ['know', 'knowledge', 'truth', 'belief', 'certain', 'doubt', 'evidence', 'proof', 'rational', 'reason'],
            'logic': ['logic', 'argument', 'premise', 'conclusion', 'valid', 'fallacy', 'inference', 'deduce', 'infer'],
            'aesthetics': ['beauty', 'art', 'aesthetic', 'taste', 'sublime', 'ugly', 'creative', 'expression', 'style'],
            'political': ['justice', 'society', 'government', 'rights', 'freedom', 'equality', 'democracy', 'power', 'law'],
            'mind': ['mind', 'consciousness', 'thought', 'perception', 'awareness', 'mental', 'cognitive', 'brain', 'soul'],
            'language': ['meaning', 'language', 'word', 'communication', 'semantics', 'syntax', 'reference', 'sign', 'symbol'],
            'religion': ['god', 'divine', 'faith', 'religion', 'spiritual', 'sacred', 'holy', 'afterlife', 'soul', 'prayer']
        }
        
        found_keywords = []
        text_lower = text.lower()
        
        for category, words in keywords.items():
            for word in words:
                if word in text_lower:
                    found_keywords.append(f"has_{category}_keyword")
                    break
        
        return found_keywords
    
    def create_training_data(self) -> Tuple[List[str], List[str]]:
        """Create training data for the model."""
        training_examples = [
            # Ethics
            ("What is the right thing to do?", "ethics"),
            ("Is it moral to lie to protect someone?", "ethics"),
            ("What makes an action good or bad?", "ethics"),
            ("Should we always tell the truth?", "ethics"),
            ("What are our moral obligations?", "ethics"),
            ("Is there objective morality?", "ethics"),
            
            # Metaphysics
            ("What is the nature of reality?", "metaphysics"),
            ("Do we have free will?", "metaphysics"),
            ("What is the meaning of existence?", "metaphysics"),
            ("Is time real or an illusion?", "metaphysics"),
            ("What is the relationship between mind and matter?", "metaphysics"),
            ("Does the universe have a purpose?", "metaphysics"),
            
            # Epistemology
            ("How do we know what we know?", "epistemology"),
            ("What is truth?", "epistemology"),
            ("Can we have certain knowledge?", "epistemology"),
            ("What is the difference between belief and knowledge?", "epistemology"),
            ("How do we justify our beliefs?", "epistemology"),
            ("Is there absolute truth?", "epistemology"),
            
            # Logic
            ("What makes an argument valid?", "logic"),
            ("How do we reason correctly?", "logic"),
            ("What are logical fallacies?", "logic"),
            ("What is the structure of good arguments?", "logic"),
            ("How do we evaluate reasoning?", "logic"),
            ("What is deductive reasoning?", "logic"),
            
            # Aesthetics
            ("What is beauty?", "aesthetics"),
            ("Is art subjective?", "aesthetics"),
            ("What makes something a work of art?", "aesthetics"),
            ("Can we judge aesthetic taste?", "aesthetics"),
            ("What is the purpose of art?", "aesthetics"),
            ("Is beauty in the eye of the beholder?", "aesthetics"),
            
            # Political Philosophy
            ("What is justice?", "political"),
            ("What makes a government legitimate?", "political"),
            ("What are human rights?", "political"),
            ("How should society be organized?", "political"),
            ("What is the role of government?", "political"),
            ("What is freedom?", "political"),
            
            # Philosophy of Mind
            ("What is consciousness?", "mind"),
            ("Do we have a soul?", "mind"),
            ("What is the relationship between mind and brain?", "mind"),
            ("Can machines think?", "mind"),
            ("What is personal identity?", "mind"),
            ("What are thoughts made of?", "mind"),
            
            # Philosophy of Language
            ("What is meaning?", "language"),
            ("How does language work?", "language"),
            ("What is the relationship between words and reality?", "language"),
            ("Can language limit thought?", "language"),
            ("What makes communication possible?", "language"),
            ("How do words refer to things?", "language"),
            
            # Philosophy of Religion
            ("Does God exist?", "religion"),
            ("What is the nature of faith?", "religion"),
            ("Can we prove God's existence?", "religion"),
            ("What is the problem of evil?", "religion"),
            ("Is there life after death?", "religion"),
            ("What is the meaning of religious experience?", "religion"),
            
            # General Philosophy
            ("What is philosophy?", "general"),
            ("Why do we philosophize?", "general"),
            ("What are the big questions?", "general"),
            ("How should we live?", "general"),
            ("What is wisdom?", "general"),
            ("What can philosophy teach us?", "general")
        ]
        
        texts, labels = zip(*training_examples)
        return list(texts), list(labels)
    
    def train(self):
        """Train the decision tree model."""
        # Get training data
        texts, labels = self.create_training_data()
        
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(processed_texts)
        
        # Add keyword features
        keyword_features = []
        for text in texts:
            keywords = self.extract_keywords(text)
            keyword_vector = [1 if f"has_{cat}_keyword" in keywords else 0 
                            for cat in self.categories[:-1]]  # Exclude 'general'
            keyword_features.append(keyword_vector)
        
        keyword_features = np.array(keyword_features)
        X_combined = np.hstack([X.toarray(), keyword_features])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train decision tree
        self.model = DecisionTreeClassifier(
            max_depth=10,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        self.save_model()
    
    def save_model(self):
        """Save the trained model and vectorizer."""
        os.makedirs('models', exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"Model saved to {self.model_path}")
        print(f"Vectorizer saved to {self.vectorizer_path}")
    
    def load_model(self):
        """Load the trained model and vectorizer."""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            return True
        return False
    
    def predict(self, text: str) -> Tuple[str, Dict[str, float]]:
        """
        Predict the philosophical category of a given text.
        Returns the predicted category and confidence scores.
        """
        if self.model is None or self.vectorizer is None:
            if not self.load_model():
                raise ValueError("Model not found. Please train the model first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Create features
        X_tfidf = self.vectorizer.transform([processed_text])
        
        # Extract keyword features
        keywords = self.extract_keywords(text)
        keyword_vector = [1 if f"has_{cat}_keyword" in keywords else 0 
                         for cat in self.categories[:-1]]
        
        # Combine features
        X_combined = np.hstack([X_tfidf.toarray(), [keyword_vector]])
        
        # Get prediction
        prediction = self.model.predict(X_combined)[0]
        
        # Get probability scores (for decision trees, we'll use the decision path)
        # For a more sophisticated approach, we could use predict_proba with a different model
        confidence_scores = {cat: 0.0 for cat in self.categories}
        confidence_scores[prediction] = 1.0
        
        return prediction, confidence_scores
    
    def get_category_description(self, category: str) -> str:
        """Get a description of the philosophical category."""
        descriptions = {
            'ethics': "Ethics and Moral Philosophy - Questions about right and wrong, moral values, and how we should live.",
            'metaphysics': "Metaphysics - Questions about the nature of reality, existence, and being.",
            'epistemology': "Epistemology - Questions about knowledge, truth, and how we know what we know.",
            'logic': "Logic and Reasoning - Questions about valid arguments, rational thinking, and inference.",
            'aesthetics': "Aesthetics - Questions about beauty, art, and aesthetic judgment.",
            'political': "Political Philosophy - Questions about justice, society, government, and rights.",
            'mind': "Philosophy of Mind - Questions about consciousness, thought, and mental phenomena.",
            'language': "Philosophy of Language - Questions about meaning, communication, and linguistic understanding.",
            'religion': "Philosophy of Religion - Questions about God, faith, and religious experience.",
            'general': "General Philosophy - Broad philosophical questions about life, wisdom, and the human condition."
        }
        return descriptions.get(category, "Unknown category")


# Training script
if __name__ == "__main__":
    categorizer = PhilosophicalCategorizer()
    print("Training philosophical categorizer...")
    categorizer.train()
    
    # Test predictions
    test_questions = [
        "Pain in heart can be caused by emotion?",
        "What is the nature of consciousness?",
        "How can we know if our beliefs are true?",
        "What makes a painting beautiful?",
        "Does God exist?"
    ]
    
    print("\n\nTesting predictions:")
    print("-" * 50)
    for question in test_questions:
        category, scores = categorizer.predict(question)
        print(f"\nQuestion: {question}")
        print(f"Category: {category}")
        print(f"Description: {categorizer.get_category_description(category)}")