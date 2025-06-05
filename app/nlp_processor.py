import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from typing import Dict, List
import string
import os

class NLPProcessor:
    def __init__(self):
        nltk_data_path = os.path.join(os.path.dirname(__file__), '..', 'nltk_data')
        os.makedirs(nltk_data_path, exist_ok=True)
        nltk.data.path.append(nltk_data_path)
        
        self._download_nltk_data()
        
        try:
            self.lemmatizer = WordNetLemmatizer()
        except:
            print("Warning: WordNetLemmatizer not available")
            self.lemmatizer = None
            
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            print("Warning: NLTK stopwords not available, using default set")
            # Fallback to a basic set of stop words
            self.stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
                'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 
                'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 
                'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 
                'am', 'is', 'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had', 
                'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
                'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 
                'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 
                'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 
                'over', 'under', 'again', 'further', 'then', 'once'
            }
    
    def _download_nltk_data(self):
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
            except LookupError:
                try:
                    print(f"Downloading NLTK resource: {name}")
                    nltk.download(name, quiet=False)
                except Exception as e:
                    print(f"Warning: Could not download {name}: {e}")
                    # Try alternate download method
                    try:
                        nltk.download(name)
                    except:
                        print(f"Failed to download {name}. Please run: python download_nltk_data.py")
    
    def process(self, text: str) -> Dict[str, any]:
        text_lower = text.lower()
        
        try:
            # Try NLTK tokenization
            tokens = word_tokenize(text)
        except:
            # Fallback to simple tokenization
            tokens = text.split()
        
        tokens_no_punct = [token for token in tokens if token not in string.punctuation]
        
        try:
            # Try NLTK lemmatization
            if self.lemmatizer:
                lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens_no_punct]
            else:
                lemmatized_tokens = [token.lower() for token in tokens_no_punct]
        except:
            # Fallback to lowercase
            lemmatized_tokens = [token.lower() for token in tokens_no_punct]
        
        filtered_tokens = [token for token in lemmatized_tokens if token.lower() not in self.stop_words]
        
        try:
            # Try NLTK POS tagging
            pos_tags = nltk.pos_tag(tokens_no_punct)
        except:
            # Fallback to simple tagging
            pos_tags = [(token, 'NN') for token in tokens_no_punct]
        
        questions_keywords = ['what', 'why', 'how', 'when', 'where', 'who', 'which']
        is_question = any(keyword in text_lower for keyword in questions_keywords) or text.strip().endswith('?')
        
        return {
            'original': text,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens,
            'lemmatized_tokens': lemmatized_tokens,
            'pos_tags': pos_tags,
            'is_question': is_question,
            'word_count': len(tokens_no_punct)
        }