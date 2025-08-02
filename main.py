# ==============================================================================
# main.py
# Main application entry point.
# ==============================================================================
import sys
import json
import os
import pickle
import torch
from PyQt6.QtWidgets import QApplication

# Import project modules
from config import Config
from utils.logger import get_logger
from utils.preprocessing import TextPreprocessor
from model.intent_classifier import IntentClassifier
from model.response_handler import ResponseHandler
from model.context_handler import ContextHandler
from gui.chatbot_gui import ChatbotGUI

# Initialize logger for the main module
logger = get_logger(__name__)

class ChatbotApp:
    """
    Main application class that orchestrates the chatbot's functionality.
    """
    def __init__(self):
        """
        Initializes the chatbot components and the GUI.
        """
        logger.info("Initializing Chatbot Application...")
        self.config = Config()
        
        # Initialize GUI to None before any potential calls to methods that use it
        self.gui = None
        
        # Initialize Data and Preprocessing
        self.data = self._load_data(self.config.DATA_PATH)
        self.preprocessor = TextPreprocessor(self.config)
        self.context_handler = ContextHandler(self.config.CONTEXT_WINDOW_SIZE)

        # Initialize Model Components
        self.intent_classifier = IntentClassifier(self.config)
        self.response_handler = ResponseHandler(self.data, self.config)
        
        # Load or train the model
        if not os.path.exists(self.config.MODEL_FILE_PATH):
            logger.warning("Model file not found. Starting initial training.")
            self.retrain_model()
        else:
            try:
                self.intent_classifier.load_model()
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}. Retraining...")
                self.retrain_model()

        # Initialize GUI
        self.app = QApplication(sys.argv)
        self.gui = ChatbotGUI(self)
        self.gui.setWindowTitle(f"{self.config.PROJECT_NAME} v{self.config.VERSION}")
        
        # Load conversation history if it exists
        self.load_history()
        
        self.gui.show()
        
        logger.info("Chatbot Application initialized and ready.")

    def _load_data(self, file_path):
        """
        Loads the intents and responses data from a JSON file.
        
        Args:
            file_path (str): The path to the JSON data file.
            
        Returns:
            dict: The loaded data.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found at: {file_path}")
            return {"intents": []}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON data from {file_path}: {e}")
            return {"intents": []}
            
    def process_input(self, user_input):
        """
        Handles user input, processes it, and generates a response.
        
        Args:
            user_input (str): The raw text input from the user.
            
        Returns:
            str: The chatbot's response.
        """
        if not user_input.strip():
            return "Please type something to start our conversation."

        # Add user query to context
        self.context_handler.add_user_query(user_input)
        
        # 1. Preprocess the user input
        preprocessed_text = self.preprocessor.preprocess(user_input)
        
        # 2. Classify the intent
        predicted_intent = self.intent_classifier.predict_intent(preprocessed_text)
        
        # 3. Generate a response
        response = self.response_handler.get_response(predicted_intent, self.context_handler.get_context())
        
        # Add bot response to context
        self.context_handler.add_bot_response(response)
        
        return response

    def retrain_model(self):
        """
        Retrains the intent classification model using the data file.
        """
        logger.info("Retraining command received. Starting model retraining...")
        try:
            self.intent_classifier.train_model(self.data, self.preprocessor)
            logger.info("Model retraining completed successfully.")
            if self.gui:
                self.gui.display_message("Bot", "Model has been successfully retrained!")
        except Exception as e:
            logger.error(f"An error occurred during model retraining: {e}", exc_info=True)
            if self.gui:
                self.gui.display_message("Bot", "An error occurred while retraining the model. Please check the logs.")

    def save_history(self):
        """
        Saves the current conversation history to a JSON file.
        """
        try:
            with open(self.config.CONVERSATION_HISTORY_PATH, 'w', encoding='utf-8') as f:
                json.dump(list(self.context_handler.get_context()), f, indent=4)
            logger.info("Conversation history saved successfully.")
            self.gui.display_message("Bot", "Conversation history has been saved.")
        except Exception as e:
            logger.error(f"Failed to save conversation history: {e}", exc_info=True)
            self.gui.display_message("Bot", "Failed to save conversation history.")

    def load_history(self):
        """
        Loads conversation history from a JSON file and displays it.
        """
        if os.path.exists(self.config.CONVERSATION_HISTORY_PATH):
            try:
                with open(self.config.CONVERSATION_HISTORY_PATH, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                self.context_handler.clear_context()
                self.gui.clear_chat()
                
                for entry in history:
                    sender = "User" if entry['role'] == 'user' else "Bot"
                    self.gui.display_message(sender, entry['text'])
                    self.context_handler.context.append(entry)
                
                logger.info("Conversation history loaded successfully.")
                self.gui.display_message("Bot", "Conversation history loaded.")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load conversation history: {e}", exc_info=True)
                self.gui.display_message("Bot", "Failed to load conversation history.")

    def run(self):
        """
        Starts the main event loop of the application.
        """
        sys.exit(self.app.exec())

if __name__ == '__main__':
    bot = ChatbotApp()
    bot.run()
s