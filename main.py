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
from admin.panel import AdminPanel
from utils.api_key_manager import APIKeyManager

class ChatbotApp:
    """
    Main application class that orchestrates the chatbot's functionality.
    """
    def __init__(self):
        """
        Initializes the chatbot components and the GUI.
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
        self.context_handler = ContextHandler(self.config.CONTEXT_WINDOW_SIZE)

        # Initialize Model Components
        self.intent_classifier = IntentClassifier(self.config)
        self.response_handler = ResponseHandler(self.data, self.config)
        self.api_key_manager = APIKeyManager()
        self._httpd = None
        self._api_thread = None
        
        self.last_unknown_query = None

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
            dict: A dictionary containing the response and other metadata.
        """
        if not user_input.strip():
            return {"response": "Please type something to start our conversation.", "intent": "none", "confidence": 1.0}

        self.context_handler.add_user_query(user_input)
        preprocessed_text = self.preprocessor.preprocess(user_input)
        try:
            predicted_intent, confidence = self.intent_classifier.predict_intent(preprocessed_text)
            # If confidence is below the threshold, classify as 'unknown'
            if confidence < self.config.CONFIDENCE_THRESHOLD:
                logger.info(f"Confidence {confidence:.2f} is below threshold {self.config.CONFIDENCE_THRESHOLD}. Intent classified as 'unknown'.")
                predicted_intent = "unknown"
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"response": "Sorry, I'm having trouble understanding right now.", "intent": "error", "confidence": 0.0}

        if predicted_intent == "unknown":
            self.last_unknown_query = user_input
            return {
                "response": "I'm not sure how to answer that. Would you like me to search Google for an answer?",
                "intent": "unknown",
                "confidence": confidence,
                "action": "confirm_google_search"
            }

        response = self.response_handler.get_response(predicted_intent, confidence, self.context_handler.get_context())
        self.context_handler.add_bot_response(response)

        return {"response": response, "intent": predicted_intent, "confidence": confidence}

    def search_last_unknown_query(self):
        """
        Performs a Google search on the last query that was classified as 'unknown'.
        """
        if not self.last_unknown_query:
            return {"response": "Error: No query to search.", "intent": "error", "confidence": 0.0}

        context = [{'role': 'user', 'text': self.last_unknown_query}]
        response_text = self.response_handler.google_fallback(context)

        self.context_handler.add_bot_response(response_text)
        self.last_unknown_query = None

        return {"response": response_text, "intent": "google_search", "confidence": 1.0}

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
                    response_data = app_ref.process_input(message)

                    # Log the API session
                    app_ref.log_api_session(user_id, api_key, payload, response_data)

                    return self._send_json(200, {
                        "user_id": user_id,
                        "response": response_data.get("response"),
                        "intent": response_data.get("intent"),
                        "confidence": response_data.get("confidence")
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

    def log_api_session(self, user_id, api_key, request_data, response_data):
        """Logs an API session to the database."""
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
        """
        Retrains the intent classification model. If background=True, runs in a separate thread and hot-swaps model on completion.
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
        # sys.exit(self.app.exec())
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)

if __name__ == '__main__':
    bot = ChatbotApp()
    bot.run()
# ==============================================================================