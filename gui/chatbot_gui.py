# ==============================================================================
# gui/chatbot_gui.py
# The PyQt6-based GUI for the chatbot.
# ==============================================================================
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QTextEdit, 
                             QLineEdit, QPushButton, QHBoxLayout, QScrollArea,
                             QFrame, QLabel, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QFont
from utils.logger import get_logger
from config import Config
import random

logger = get_logger(__name__)

class ChatbotGUI(QMainWindow):
    """
    A graphical user interface for the chatbot using PyQt6.
    """
    def __init__(self, parent=None):
        # The parent is the ChatbotApp instance, but we don't pass it to QMainWindow
        # since ChatbotApp is not a QWidget.
        super().__init__() 
        self.app_logic = parent
        self.config = Config()
        self.current_theme = "light"
        
        self.setup_ui()
        self.apply_theme(self.current_theme)
        logger.info("Chatbot GUI initialized.")
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        
        self.retrain_button = QPushButton("Retrain Model")
        self.retrain_button.clicked.connect(self.app_logic.retrain_model)
        header_layout.addWidget(self.retrain_button)
        
        self.save_history_button = QPushButton("Save History")
        self.save_history_button.clicked.connect(self.app_logic.save_history)
        header_layout.addWidget(self.save_history_button)
        
        self.load_history_button = QPushButton("Load History")
        self.load_history_button.clicked.connect(self.app_logic.load_history)
        header_layout.addWidget(self.load_history_button)
        
        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)
        
        main_layout.addLayout(header_layout)
        
        self.chat_area = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_area)
        main_layout.addWidget(self.scroll_area)
        
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        if not self.app_logic.context_handler.get_context():
            self.display_message("Bot", "Hello! How can I help you today?")
        
    def apply_theme(self, theme_name):
        theme = self.config.THEMES.get(theme_name, self.config.THEMES['light'])
        
        style = f"""
            QMainWindow {{
                background-color: {theme['window_bg']};
            }}
            QScrollArea {{
                border: 1px solid {theme['border_color']};
                border-radius: 10px;
                background-color: {theme['chat_bg']};
            }}
            QLineEdit {{
                background-color: {theme['input_bg']};
                color: {theme['input_text']};
                border: 1px solid {theme['border_color']};
                border-radius: 10px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme['bot_bubble_bg']};
                color: {theme['bot_text_color']};
                border: none;
                border-radius: 10px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {theme['bot_bubble_bg']};
                opacity: 0.8;
            }}
        """
        self.setStyleSheet(style)
        self.chat_area.setStyleSheet(f"background-color: {theme['chat_bg']};")
        self.current_theme = theme_name
        logger.info(f"Theme set to '{theme_name}'.")

    def toggle_theme(self):
        if self.current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")
            
    def display_message(self, sender, message):
        theme = self.config.THEMES.get(self.current_theme)
        bubble_color = theme['user_bubble_bg'] if sender == "User" else theme['bot_bubble_bg']
        text_color = theme['user_text_color'] if sender == "User" else theme['bot_text_color']
        
        bubble_frame = QFrame()
        bubble_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bubble_color};
                border-radius: 15px;
                padding: 10px;
            }}
        """)
        
        message_label = QLabel(message)
        message_label.setStyleSheet(f"color: {text_color};")
        message_label.setWordWrap(True)
        
        bubble_layout = QVBoxLayout(bubble_frame)
        bubble_layout.addWidget(message_label)
        
        container_widget = QWidget()
        container_layout = QHBoxLayout(container_widget)
        
        if sender == "User":
            container_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
            container_layout.addWidget(bubble_frame)
        else:
            container_layout.addWidget(bubble_frame)
            container_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        
        self.chat_layout.addWidget(container_widget)
        
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()))

    def clear_chat(self):
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
    def send_message(self):
        user_text = self.user_input.text()
        if user_text:
            self.display_message("User", user_text)
            
            bot_response = self.app_logic.process_input(user_text)
            self.display_message("Bot", bot_response)
            
            self.user_input.clear()
