
# ==============================================================================
# config.py
# Centralized configuration file for the project.
# ==============================================================================
import os

class Config:
    """
    Holds all the configuration settings for the chatbot.
    """
    # ==================== GENERAL CONFIG ====================
    PROJECT_NAME = "Intelligent Chatbot"
    VERSION = "1.1.0"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ==================== DATA CONFIG ====================
    DATA_PATH = os.path.join(BASE_DIR, 'data', 'intents.json')
    
    # ==================== CONVERSATION HISTORY ====================
    CONVERSATION_HISTORY_PATH = os.path.join(BASE_DIR, 'conversations.json')

    # ==================== PREPROCESSING CONFIG ====================
    USE_LOWERCASE = True
    USE_STOPWORD_REMOVAL = True
    USE_LEMMATIZATION = True
    
    CUSTOM_STOPWORDS = {"a", "an", "the", "is", "are", "i", "you", "am"}

    # ==================== MODEL CONFIG ====================
    MODEL_FILE_PATH = os.path.join(BASE_DIR, 'model', 'intent_classifier.pkl')
    VECTORIZER_FILE_PATH = os.path.join(BASE_DIR, 'model', 'vectorizer.pkl')
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

    # ==================== GUI CONFIG ====================
    GUI_WIDTH = 800
    GUI_HEIGHT = 600
    
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
