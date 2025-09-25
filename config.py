
# ==============================================================================
# config.py
# Centralized configuration file for the project.
# ==============================================================================
import os

class Config:
    # ==================== UI CONFIG ====================
    DARK_MODE = False
    """
    Holds all the configuration settings for the chatbot.
    """
    # ==================== GENERAL CONFIG ====================
    PROJECT_NAME = "Intelligent Chatbot"
    VERSION = "1.2.0"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ==================== DATA CONFIG ====================
    DATA_PATH = os.path.join(BASE_DIR, 'data', 'intents.json')
    INTENTS_DIR = os.path.join(BASE_DIR, 'data', 'intents')
    
    # ==================== CONVERSATION HISTORY ====================
    CONVERSATION_HISTORY_PATH = os.path.join(BASE_DIR, 'conversations.json')

    # ==================== PREPROCESSING CONFIG ====================
    USE_LOWERCASE = True
    USE_STOPWORD_REMOVAL = True
    USE_LEMMATIZATION = True
    
    CUSTOM_STOPWORDS = {"a", "an", "the", "is", "are", "i", "you", "am"}

    # ==================== MODEL CONFIG ====================
    MODELS_DIR = os.path.join(BASE_DIR, 'model')
    MODEL_FILE_PATH = os.path.join(MODELS_DIR, 'svm', 'intent_classifier.pkl')
    VECTORIZER_FILE_PATH = os.path.join(MODELS_DIR, 'svm', 'vectorizer.pkl')
    BERT_MODEL_PATH = "bert-base-uncased"
    
    # Model type can be 'svm' or 'bert'
    MODEL_TYPE = 'svm'
    
    # BERT-specific parameters
    BERT_BATCH_SIZE = 16
    BERT_EPOCHS = 3
    BERT_LEARNING_RATE = 2e-5
    
    # Context Handler
    CONTEXT_WINDOW_SIZE = 3
    
    # Enable generative model response hook
    ENABLE_GENERATIVE_RESPONSE = False
    # Enable Google fallback for online search
    ENABLE_GOOGLE_FALLBACK = True
    # Maximum number of Google results to fetch per query
    GOOGLE_MAX_RESULTS = 5
    # Cache duration for Google search results (in seconds)
    GOOGLE_CACHE_DURATION = 3600

    # ==================== GUI CONFIG ====================
    GUI_WIDTH = 800
    GUI_HEIGHT = 600
    GUI_title = "Intelligent Chatbot"
    # GUI Themes


    THEMES = {
        "light": {
            "window_bg": "#f0f0f0",
            "chat_bg": "#ffffff",
            "user_bubble_bg": "#e0e0e0",
            "bot_bubble_bg": "#4a90e2",
            "user_text_color": "#000000",
            "bot_text_color": "#ffffff",
            "input_bg": "#ffffff",
            "input_text": "#000000",
            "border_color": "#cccccc",
        },
        "dark": {
            "window_bg": "#2c2c2c",
            "chat_bg": "#1e1e1e",
            "user_bubble_bg": "#444444",
            "bot_bubble_bg": "#007acc",
            "user_text_color": "#ffffff",
            "bot_text_color": "#ffffff",
            "input_bg": "#333333",
            "input_text": "#ffffff",
            "border_color": "#555555",
        }
    }

    # ==================== LOGGING CONFIG ====================
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    LOG_FILE_PREFIX = "app"
    LOG_LEVEL = "INFO" # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_ROTATION_SIZE_MB = 10

    # Add to Config class:

    def load_from_env(self):
        self.MODEL_TYPE = os.getenv("MODEL_TYPE", self.MODEL_TYPE)
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.BERT_MODEL_PATH = os.getenv("BERT_MODEL_PATH", self.BERT_MODEL_PATH)
        self.BERT_BATCH_SIZE = int(os.getenv("BERT_BATCH_SIZE", self.BERT_BATCH_SIZE))
        self.BERT_EPOCHS = int(os.getenv("BERT_EPOCHS", self.BERT_EPOCHS))
        self.BERT_LEARNING_RATE = float(os.getenv("BERT_LEARNING_RATE", self.BERT_LEARNING_RATE))
        # Optional override for intents directory
        self.INTENTS_DIR = os.getenv("INTENTS_DIR", self.INTENTS_DIR)
        # API server
        self.API_HOST = os.getenv("API_HOST", getattr(self, 'API_HOST', '127.0.0.1'))
        self.API_PORT = int(os.getenv("API_PORT", getattr(self, 'API_PORT', 8080)))
        # Allow toggling Google fallback and related settings at runtime
        self.ENABLE_GOOGLE_FALLBACK = self._get_bool_env("ENABLE_GOOGLE_FALLBACK", self.ENABLE_GOOGLE_FALLBACK)
        self.GOOGLE_MAX_RESULTS = int(os.getenv("GOOGLE_MAX_RESULTS", self.GOOGLE_MAX_RESULTS))
        self.GOOGLE_CACHE_DURATION = int(os.getenv("GOOGLE_CACHE_DURATION", self.GOOGLE_CACHE_DURATION))

    def __init__(self):
        self.load_from_env()  # Call first to allow overrides
        # The rest of your existing config stays the same

    @staticmethod
    def _get_bool_env(var, default):
        val = os.getenv(var)
        if val is None:
            return default
        return val.lower() in ("1", "true", "yes", "on")