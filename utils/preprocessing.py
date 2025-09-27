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

# Set up a logger for this module
logger = get_logger(__name__)

# --- NLTK Resource Management ---
def download_nltk_resource(resource_name, resource_path):
    """Downloads an NLTK resource if it is not already present.

    Args:
        resource_name (str): The name of the resource to download (e.g., 'punkt').
        resource_path (str): The path where NLTK looks for the resource.
    """
    try:
        nltk.data.find(resource_path)
        logger.debug(f"NLTK resource '{resource_name}' found.")
    except LookupError:
        logger.info(f"NLTK resource '{resource_name}' not found. Downloading...")
        try:
            nltk.download(resource_name, quiet=True)
            logger.info(f"Successfully downloaded NLTK resource: {resource_name}")
        except Exception as e:
            logger.error(f"Failed to download NLTK resource '{resource_name}': {e}", exc_info=True)
            # Depending on the resource, you might want to exit or raise an exception
            # For now, we'll log the error and continue.

# List of required NLTK resources and their paths
REQUIRED_NLTK_RESOURCES = {
    'punkt': 'tokenizers/punkt',
    'wordnet': 'corpora/wordnet',
    'stopwords': 'corpora/stopwords',
    'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
}

# Download all required resources at startup
for name, path in REQUIRED_NLTK_RESOURCES.items():
    download_nltk_resource(name, path)

class TextPreprocessor:
    """Handles text preprocessing tasks like tokenization and normalization.

    This class provides a structured way to clean and prepare text data
    before it is fed into the model.
    """
    def __init__(self, config):
        """Initializes the TextPreprocessor.

        Args:
            config (Config): The application's configuration object.
        """
        self.config = config
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        if self.config.USE_STOPWORD_REMOVAL and self.config.CUSTOM_STOPWORDS:
            self.stop_words.update(self.config.CUSTOM_STOPWORDS)
        logger.info("Text preprocessor initialized.")

    def tokenize(self, text):
        """Tokenizes a given text into words.

        Args:
            text (str): The text to tokenize.

        Returns:
            list: A list of tokens (words).
        """
        return word_tokenize(text)

    def preprocess(self, text):
        """Performs a full preprocessing pipeline on a given text.

        The pipeline includes tokenization, lowercasing, punctuation and
        stopword removal, and lemmatization, based on the configuration.

        Args:
            text (str): The text to preprocess.

        Returns:
            list: A list of preprocessed tokens.
        """
        tokens = self.tokenize(text)
        tokens = [token.lower() for token in tokens if token not in string.punctuation]
            
        if self.config.USE_STOPWORD_REMOVAL:
            tokens = [token for token in tokens if token not in self.stop_words]
            
        if self.config.USE_LEMMATIZATION:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
        return tokens
