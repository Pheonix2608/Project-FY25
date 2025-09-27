# ==============================================================================
# main.py
# Main application entry point.
# ==============================================================================

import sys
import json
import os
import pickle
import torch
from datetime import datetime
from PyQt6.QtWidgets import QApplication
import threading
import uvicorn
from api.server import app as fastapi_app, set_chatbot_app

# Import project modules
from config import Config
from utils.logger import get_logger
from utils.preprocessing import TextPreprocessor
from utils.data_loader import load_all_intents
from model.intent_classifier import IntentClassifier
from model.response_handler import ResponseHandler
from model.context_handler import ContextHandler
from model.ner_extractor import NERExtractor
from admin.panel import AdminPanel
from utils.api_key_manager import APIKeyManager

class ChatbotApp:
    """The main application class for the chatbot.

    This class orchestrates the entire application, including initializing
    the configuration, models, GUI, and API server. It manages the core
    logic for processing user input and generating responses.
    """
    def __init__(self):
        """Initializes the chatbot application.

        This method sets up all necessary components, including the logger,
        data preprocessor, model classifiers, and handlers. It also loads
        the trained model or initiates training if a model is not found.
        """
        self.config = Config()
        
        # Initialize logger
        global logger
        logger = get_logger(__name__)

        logger.info("Initializing Chatbot Application...")

        # Initialize GUI to None before any potential calls to methods that use it
        self.gui = None
        
        # Initialize Data and Preprocessing
        self.data = self._load_data(self.config.DATA_PATH)
        self.preprocessor = TextPreprocessor(self.config)

        # Session management
        self.user_sessions = {}

        # Initialize Model Components
        self.intent_classifier = IntentClassifier(self.config)
        self.response_handler = ResponseHandler(self.data, self.config)
        self.ner_extractor = NERExtractor()
        self.api_key_manager = APIKeyManager()

        # Set the chatbot app instance for the FastAPI server
        set_chatbot_app(self)

        # Database is initialized in the main block

        # Load or train the model
        try:
            loaded = self.intent_classifier.load_model()
            if not loaded:
                logger.warning("Model files not found. Starting initial training in background.")
                self.retrain_model(background=True)
            else:
                logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}. Retraining in background...")
            self.retrain_model(background=True)

        # Initialize GUI
        # self.app = QApplication(sys.argv)
        # self.gui = AdminPanel(self)
        # self.gui.setWindowTitle(f"{self.config.PROJECT_NAME} v{self.config.VERSION} - Admin Panel")
        
        # self.gui.show()

        # The API server is started in a background thread.

        # The API server is started in a background thread.
        
        logger.info("Chatbot Application initialized and ready.")

        # Start background API server
        try:
            self.start_api_server()
            logger.info("Background API server started.")
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")

    def get_or_create_session(self, user_id: str):
        """Retrieves an existing session for a user or creates a new one.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            dict: The user's session dictionary.
        """
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "context_handler": ContextHandler(self.config.CONTEXT_WINDOW_SIZE),
                "google_search_confirmation_pending": False,
                "session_google_search_preference": None,
                "last_unknown_query": None,
            }
            logger.info(f"Created new session for user_id: {user_id}")
        return self.user_sessions[user_id]

    def _load_data(self, file_path):
        """Loads intent data from the intents directory.

        Args:
            file_path (str): A deprecated argument kept for compatibility.

        Returns:
            dict: A dictionary containing the loaded intent data.
        """
        try:
            intents_dir = getattr(self.config, 'INTENTS_DIR', None)
            if intents_dir and os.path.isdir(intents_dir):
                return load_all_intents(intents_dir)
            # Fallback to legacy single file if directory missing
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Intents not found in directory or file. Checked dir: {getattr(self.config, 'INTENTS_DIR', None)}, file: {file_path}")
            return {"intents": []}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON intents: {e}")
            return {"intents": []}
            
    def process_input(self, user_id: str, user_input: str):
        """Handles user input, processes it, and generates a response.

        This is the core logic function that takes a user's message,
        classifies the intent, and returns a complete response dictionary.

        Args:
            user_id (str): The unique identifier for the user.
            user_input (str): The raw text input from the user.

        Returns:
            dict: A dictionary containing the response, intent, confidence,
                and extracted entities.
        """
        session = self.get_or_create_session(user_id)
        context_handler = session["context_handler"]

        # Extract entities from the user input
        entities = self.ner_extractor.extract_entities(user_input)

        if not user_input.strip():
            return {"response": "Please type something to start our conversation.", "intent": "none", "confidence": 1.0, "entities": entities}

        # Handle Google Search confirmation flow
        if session["google_search_confirmation_pending"]:
            if user_input.lower() in ['yes', 'y']:
                session["session_google_search_preference"] = True
                session["google_search_confirmation_pending"] = False
                query = session["last_unknown_query"]
                session["last_unknown_query"] = None

                response_text = self.response_handler.google_fallback(query)

                context_handler.add_user_query(query)
                context_handler.add_bot_response(response_text)

                return {"response": response_text, "intent": "google_search", "confidence": 1.0, "entities": entities}
            elif user_input.lower() in ['no', 'n']:
                session["session_google_search_preference"] = False
                session["google_search_confirmation_pending"] = False
                session["last_unknown_query"] = None
                response = "Okay, I won't search. How else can I help you?"
                context_handler.add_user_query(user_input)
                context_handler.add_bot_response(response)
                return {"response": response, "intent": "default", "confidence": 1.0, "entities": entities}
            else:
                response = "Please answer with 'yes' or 'no'. Would you like me to search Google for an answer?"
                return {"response": response, "intent": "unknown_google_confirm", "confidence": 1.0, "entities": entities}

        context_handler.add_user_query(user_input)
        preprocessed_text = self.preprocessor.preprocess(user_input)

        try:
            predicted_intent, confidence = self.intent_classifier.predict_intent(preprocessed_text)
            if confidence < self.config.CONFIDENCE_THRESHOLD:
                logger.info(f"Confidence {confidence:.2f} is below threshold {self.config.CONFIDENCE_THRESHOLD}. Intent classified as 'unknown'.")
                predicted_intent = "unknown"
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"response": "Sorry, I'm having trouble understanding right now.", "intent": "error", "confidence": 0.0, "entities": entities}

        if predicted_intent == "unknown":
            if session["session_google_search_preference"] is True:
                response = self.response_handler.google_fallback(user_input)
            elif session["session_google_search_preference"] is False:
                response = self.response_handler.get_response("default", 1.0, context_handler.get_context(), entities=entities)
            else:
                session["google_search_confirmation_pending"] = True
                session["last_unknown_query"] = user_input
                response = "I'm not sure how to answer that. Would you like me to search Google for an answer? (yes/no)"
                return {"response": response, "intent": "unknown_google_confirm", "confidence": confidence, "entities": entities}
        else:
            response = self.response_handler.get_response(predicted_intent, confidence, context_handler.get_context(), entities=entities)

        context_handler.add_bot_response(response)

        return {"response": response, "intent": predicted_intent, "confidence": confidence, "entities": entities}

    # ==================== API KEYS ====================
    def generate_api_key(self, user_id: str = "default_user") -> str:
        """Generates an API key for a user.

        Args:
            user_id (str): The ID of the user for whom to generate the key.

        Returns:
            str: The newly generated API key, or an empty string on failure.
        """
        try:
            api_key = self.api_key_manager.generate_api_key(user_id)
            logger.info(f"Generated API key for user_id={user_id}")
            return api_key
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            return ""


    # ==================== HTTP API ====================
    def start_api_server(self):
        """Starts the FastAPI server in a background thread."""
        config = uvicorn.Config(
            fastapi_app,
            host=getattr(self.config, 'API_HOST', '0.0.0.0'),
            port=getattr(self.config, 'API_PORT', 8080),
            log_level="info",
            timeout_keep_alive=5
        )
        self.server = uvicorn.Server(config)
        self._api_thread = threading.Thread(target=self.server.run, daemon=False)
        self._api_thread.start()

    def stop_api_server(self):
        """Stops the running FastAPI server gracefully."""
        if hasattr(self, 'server'):
            self.server.should_exit = True
            if hasattr(self, '_api_thread'):
                self._api_thread.join(timeout=6)
                logger.info("API server thread joined.")

    def log_api_session(self, user_id, api_key, request_data, response_data):
        """Logs an API interaction to the database.

        Args:
            user_id (str): The ID of the user making the request.
            api_key (str): The API key used for the request.
            request_data (dict): The data sent in the request body.
            response_data (dict): The data returned in the response.
        """
        try:
            from utils.database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO api_sessions (user_id, api_key, request_data, response_data)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        api_key,
                        json.dumps(request_data),
                        json.dumps(response_data)
                    )
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log API session to database: {e}", exc_info=True)

    def retrain_model(self, background=False):
        """Retrains the intent classification model.

        This can be run in the foreground (blocking) or in a background
        thread to avoid freezing the application.

        Args:
            background (bool): If True, retraining runs in a background thread.
        """
        def _retrain():
            logger.info("[Retrain] Background retraining started...")
            try:
                new_classifier = IntentClassifier(self.config)
                new_classifier.train_model(self.data, self.preprocessor)
                logger.info("[Retrain] Model retraining completed. Hot-swapping model.")
                self.intent_classifier = new_classifier
                if self.gui:
                    self.gui.display_message("Bot", "Model retrained and updated in background!")
            except Exception as e:
                logger.error(f"[Retrain] Error during background retraining: {e}", exc_info=True)
                if self.gui:
                    self.gui.display_message("Bot", "Background retraining failed. See logs.")

        if background:
            logger.info("[Retrain] Initiating background retraining...")
            retrain_thread = threading.Thread(target=_retrain, daemon=True)
            retrain_thread.start()
        else:
            logger.info("Retraining command received. Starting model retraining...")
            try:
                self.intent_classifier = IntentClassifier(self.config)
                self.intent_classifier.train_model(self.data, self.preprocessor)
                logger.info("Model retraining completed successfully.")
                if self.gui:
                    self.gui.display_message("Bot", "Model has been successfully retrained!")
            except Exception as e:
                logger.error(f"An error occurred during model retraining: {e}", exc_info=True)
                if self.gui:
                    self.gui.display_message("Bot", "An error occurred while retraining the model. Please check the logs.")


    def get_sessions_dir(self):
        """Gets the directory where chat sessions are stored.

        Returns:
            str: The absolute path to the sessions directory.
        """
        sessions_dir = os.path.join(self.config.BASE_DIR, 'data', 'sessions')
        os.makedirs(sessions_dir, exist_ok=True)
        return sessions_dir

    def list_sessions(self):
        """Lists all saved chat session files.

        Returns:
            list: A sorted list of session filenames.
        """
        sessions_dir = self.get_sessions_dir()
        return sorted([f for f in os.listdir(sessions_dir) if f.endswith('.json')])

    def save_history(self, session_name=None):
        """Saves the current conversation history to a session file.

        Args:
            session_name (str, optional): The name for the session file.
                If None, a timestamped name is generated.
        """
        try:
            if session_name is None:
                session_name = datetime.now().strftime('session_%Y%m%d_%H%M%S.json')
            sessions_dir = self.get_sessions_dir()
            session_path = os.path.join(sessions_dir, session_name)
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.context_handler.get_context()), f, indent=4)
            logger.info(f"Session saved: {session_path}")
            self.gui.display_message("Bot", f"Session saved as {session_name}.")
            if hasattr(self.gui, 'refresh_sessions_sidebar'):
                self.gui.refresh_sessions_sidebar()
        except Exception as e:
            logger.error(f"Failed to save session: {e}", exc_info=True)
            self.gui.display_message("Bot", "Failed to save session.")


    def load_history(self, session_name=None):
        """Loads a conversation history from a session file.

        Args:
            session_name (str, optional): The name of the session file to load.
                If None, the latest session is loaded.
        """
        try:
            sessions = self.list_sessions()
            if not sessions:
                self.gui.display_message("Bot", "No session history found.")
                return
            if session_name is None:
                session_name = sessions[-1]  # Load latest session by default
            session_path = os.path.join(self.get_sessions_dir(), session_name)
            with open(session_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            self.context_handler.clear_context()
            self.gui.clear_chat()
            for entry in history:
                if isinstance(entry, dict):
                    sender = "User" if entry.get('role', 'user') == 'user' else "Bot"
                    self.gui.display_message(sender, entry.get('text', str(entry)))
                    self.context_handler.context.append(entry)
                else:
                    # If entry is a string or other type, skip or handle as needed
                    continue
            logger.info(f"Session loaded: {session_name}")
            self.gui.display_message("Bot", f"Session '{session_name}' loaded.")
        except Exception as e:
            logger.error(f"Failed to load session: {e}", exc_info=True)
            self.gui.display_message("Bot", "Failed to load session.")

    def run(self):
        """Starts the main application loop and handles graceful shutdown."""
        try:
            # Keep the main thread alive
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received.")
        finally:
            logger.info("Shutting down API server...")
            self.stop_api_server()
            logger.info("Application shut down.")

if __name__ == '__main__':
    bot = ChatbotApp()
    bot.run()
# ==============================================================================