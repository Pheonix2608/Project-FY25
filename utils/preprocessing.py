# ==============================================================================
# utils/preprocessing.py
# Preprocessing script for handling text normalization and tokenization.
# ==============================================================================
import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os

from utils.logger import get_logger

import nltk
from urllib.error import URLError

resources = {
    'corpora/wordnet': 'wordnet',
    'corpora/stopwords': 'stopwords',
    'tokenizers/punkt': 'punkt',
    'taggers/averaged_perceptron_tagger': 'averaged_perceptron_tagger'
}

for path, name in resources.items():
    try:
        nltk.data.find(path)
    except LookupError:
        try:
            print(f"Downloading missing resource: {name}")
            nltk.download(name)
        except URLError as e:
            print(f"Network error while downloading {name}: {e}")
        except Exception as e:
            print(f"Unexpected error while downloading {name}: {e}")

logger = get_logger(__name__)

class TextPreprocessor:
    """
    A class to handle text preprocessing tasks for the chatbot.
    """
    def __init__(self, config):
        self.config = config
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        if self.config.USE_STOPWORD_REMOVAL and self.config.CUSTOM_STOPWORDS:
            self.stop_words.update(self.config.CUSTOM_STOPWORDS)
        logger.info("Text preprocessor initialized.")

    def tokenize(self, text):
        return word_tokenize(text)

    def preprocess(self, text):
        tokens = self.tokenize(text)
        tokens = [token.lower() for token in tokens if token not in string.punctuation]
            
        if self.config.USE_STOPWORD_REMOVAL:
            tokens = [token for token in tokens if token not in self.stop_words]
            
        if self.config.USE_LEMMATIZATION:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
        return tokens
