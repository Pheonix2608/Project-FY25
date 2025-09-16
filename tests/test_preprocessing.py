import sys
import os
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import TextPreprocessor

class MockConfig:
    """A mock config class for testing purposes."""
    def __init__(self):
        self.USE_LOWERCASE = True
        self.USE_STOPWORD_REMOVAL = True
        self.USE_LEMMATIZATION = True
        self.CUSTOM_STOPWORDS = {"a", "an", "the", "is", "are", "i", "you", "am"}

@pytest.fixture
def preprocessor():
    """Pytest fixture to create a TextPreprocessor instance."""
    return TextPreprocessor(MockConfig())

def test_preprocess_full(preprocessor):
    """Test the full preprocessing pipeline."""
    text = "Hello there, I am running and testing this."
    expected = ['hello', 'running', 'testing']
    result = preprocessor.preprocess(text)
    assert result == expected

def test_preprocess_no_stopwords(preprocessor):
    """Test preprocessing without stopword removal."""
    preprocessor.config.USE_STOPWORD_REMOVAL = False
    text = "Hello there, I am running and testing this."
    expected = ['hello', 'there', 'i', 'am', 'running', 'and', 'testing', 'this']
    result = preprocessor.preprocess(text)
    assert result == expected

def test_preprocess_no_lemmatization(preprocessor):
    """Test preprocessing without lemmatization."""
    preprocessor.config.USE_LEMMATIZATION = False
    text = "Hello there, I am running and testing this."
    expected = ['hello', 'running', 'testing']
    result = preprocessor.preprocess(text)
    assert result == expected # Lemmatization doesn't change these words

def test_preprocess_empty_string(preprocessor):
    """Test preprocessing an empty string."""
    text = ""
    expected = []
    result = preprocessor.preprocess(text)
    assert result == expected

def test_preprocess_punctuation_only(preprocessor):
    """Test preprocessing a string with only punctuation."""
    text = "!@#$%^&*()"
    expected = []
    result = preprocessor.preprocess(text)
    assert result == expected
