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
from http.server import BaseHTTPRequestHandler, HTTPServer

# Import project modules
from config import Config
from utils.logger import get_logger
from utils.preprocessing import TextPreprocessor
from utils.data_loader import load_all_intents
from model.intent_classifier import IntentClassifier
from model.response_handler import ResponseHandler
from model.context_handler import ContextHandler
from gui.chatbot_gui import ChatbotGUI
from utils.api_key_manager import APIKeyManager

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
        self.api_key_manager = APIKeyManager()
        self._httpd = None
        self._api_thread = None
        
        # Load or train the model
        try:
            loaded = self.intent_classifier.load_model()
            if not loaded:
                logger.warning("Model files not found. Starting initial training.")
                self.retrain_model()
            else:
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

        # Start background API server
        try:
            self.start_api_server()
            logger.info("Background API server started.")
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")

    def _load_data(self, file_path):
        """
        Loads the intents and responses data from the intents directory.
        
        Args:
            file_path (str): Deprecated. Kept for compatibility.
            
        Returns:
            dict: The loaded data.
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

    # ==================== API KEYS ====================
    def generate_api_key(self, user_id: str = "default_user") -> str:
        """
        Generates an API key for a given user and returns the plaintext key once.
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
        host = getattr(self.config, 'API_HOST', '0.0.0.0')
        port = getattr(self.config, 'API_PORT', 8080)

        app_ref = self

        class ChatRequestHandler(BaseHTTPRequestHandler):
            def _send_json(self, code, payload):
                try:
                    body = json.dumps(payload).encode('utf-8')
                except Exception:
                    body = b"{}"
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path == '/':
                    return self._send_json(200, {
                        "status": "ok",
                        "message": "Chatbot API running",
                        "endpoints": [
                            {"path": "/chat", "method": "POST", "headers": ["X-API-Key"], "body": {"message": "string"}}
                        ]
                    })
                if self.path == '/chat':
                    return self._send_json(405, {"error": "Method Not Allowed", "use": "POST /chat"})
                return self._send_json(404, {"error": "Not Found"})

            def do_OPTIONS(self):
                self.send_response(204)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
                self.end_headers()

            def do_POST(self):
                try:
                    if self.path != '/chat':
                        return self._send_json(404, {"error": "Not Found"})

                    content_length = int(self.headers.get('Content-Length', '0'))
                    raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
                    try:
                        payload = json.loads(raw.decode('utf-8'))
                    except Exception:
                        return self._send_json(400, {"error": "Invalid JSON"})

                    api_key = self.headers.get('X-API-Key') or payload.get('api_key')
                    message = payload.get('message', '')

                    if not api_key:
                        return self._send_json(401, {"error": "Missing API key"})
                    if not message:
                        return self._send_json(400, {"error": "Missing message"})

                    user_id = app_ref.api_key_manager.verify_api_key(api_key)
                    if not user_id:
                        return self._send_json(403, {"error": "Invalid or expired API key"})

                    # Process input using the app's pipeline
                    response_text = app_ref.process_input(message)
                    return self._send_json(200, {
                        "user_id": user_id,
                        "response": response_text
                    })
                except Exception as e:
                    logger.error(f"API error: {e}")
                    return self._send_json(500, {"error": "Internal Server Error"})

        # Create server bound to host:port
        self._httpd = HTTPServer((host, port), ChatRequestHandler)

        def serve():
            try:
                self._httpd.serve_forever()
            except Exception as e:
                logger.error(f"HTTP server stopped: {e}")

        self._api_thread = threading.Thread(target=serve, daemon=True)
        self._api_thread.start()

    def stop_api_server(self):
        try:
            if self._httpd:
                self._httpd.shutdown()
                self._httpd.server_close()
                self._httpd = None
        except Exception:
            pass

    def retrain_model(self):
        """
        Retrains the intent classification model using the data file.
        """
        logger.info("Retraining command received. Starting model retraining...")
        try:
            # Rebuild classifier according to current config.MODEL_TYPE
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
        sessions_dir = os.path.join(self.config.BASE_DIR, 'data', 'sessions')
        os.makedirs(sessions_dir, exist_ok=True)
        return sessions_dir

    def list_sessions(self):
        sessions_dir = self.get_sessions_dir()
        return sorted([f for f in os.listdir(sessions_dir) if f.endswith('.json')])

    def save_history(self, session_name=None):
        """
        Saves the current conversation history to a new session file (timestamped if not provided).
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
        """
        Loads conversation history from a session file (default: latest session).
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
        """
        Starts the main event loop of the application.
        """
        sys.exit(self.app.exec())

if __name__ == '__main__':
    bot = ChatbotApp()
    bot.run()
# ==============================================================================