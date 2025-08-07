# chatbot_gui.py (Revamped GUI with JSON Export)

"""
This module defines the ChatbotGUI class which provides the graphical user interface
for interacting with the chatbot. It supports theme switching, model switching,
chat history saving/loading, and exporting chat logs as text or JSON.
"""

import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QComboBox, QFileDialog, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer

class ChatbotGUI(QWidget):
    """Main GUI class for the chatbot application."""

    def __init__(self, app):
        """
        Initialize the GUI, set geometry, theme, and build layout.

        Args:
            app (ChatbotApp): The main application instance.
        """
        super().__init__()
        self.app_instance = app
        self.config = app.config
        self.current_theme = "light"
        self.conversation_log = []  # Store chat as structured data

        self.setGeometry(100, 100, self.config.GUI_WIDTH, self.config.GUI_HEIGHT)
        self.init_ui()
        self.apply_theme(self.current_theme)

    def init_ui(self):
        """Initializes all UI components and layouts."""
        self.setStyleSheet("font-size: 14px;")

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Input area
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        # Buttons and their actions
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.app_instance.save_history)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.app_instance.load_history)

        self.export_button = QPushButton("Export Chat")
        self.export_button.clicked.connect(self.export_chat)

        self.export_json_button = QPushButton("Export JSON")
        self.export_json_button.clicked.connect(self.export_chat_json)

        self.retrain_button = QPushButton("Retrain Model")
        self.retrain_button.clicked.connect(self.app_instance.retrain_model)

        # Typing indicator
        self.typing_label = QLabel("")

        # Dropdown for model selection
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["svm", "bert"])
        self.model_dropdown.setCurrentText(self.config.MODEL_TYPE)
        self.model_dropdown.currentTextChanged.connect(self.switch_model)

        # Theme switcher
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["light", "dark"])
        self.theme_dropdown.setCurrentText(self.current_theme)
        self.theme_dropdown.currentTextChanged.connect(self.switch_theme)

        # Layouts
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.send_button)
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.export_button)
        btn_layout.addWidget(self.export_json_button)
        btn_layout.addWidget(self.retrain_button)

        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Model:"))
        settings_layout.addWidget(self.model_dropdown)
        settings_layout.addWidget(QLabel("Theme:"))
        settings_layout.addWidget(self.theme_dropdown)
        settings_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(settings_layout)
        layout.addWidget(self.chat_display)
        layout.addWidget(self.typing_label)
        layout.addWidget(self.input_field)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def display_message(self, sender, message):
        """Displays a message in the chat window with a timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
        self.conversation_log.append({"time": timestamp, "sender": sender, "text": message})

    def clear_chat(self):
        """Clears the chat display and resets conversation log."""
        self.chat_display.clear()
        self.conversation_log.clear()

    def send_message(self):
        """Handles user input and triggers bot response with a typing delay."""
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.display_message("User", user_input)
        self.input_field.clear()
        self.typing_label.setText("Bot is typing...")
        QTimer.singleShot(1000, lambda: self.generate_response(user_input))

    def generate_response(self, user_input):
        """Gets response from bot and displays it."""
        response = self.app_instance.process_input(user_input)
        self.typing_label.clear()
        self.display_message("Bot", response)

    def switch_model(self, new_model):
        """Handles logic for switching between different model types."""
        if new_model != self.config.MODEL_TYPE:
            reply = QMessageBox.question(
                self, "Switch Model",
                f"Switch model to '{new_model}' and restart training?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.config.MODEL_TYPE = new_model
                self.app_instance.retrain_model()
                self.display_message("Bot", f"Switched to '{new_model}' model and retrained.")

    def switch_theme(self, new_theme):
        """Applies the selected GUI theme."""
        if new_theme in self.config.THEMES:
            self.current_theme = new_theme
            self.apply_theme(new_theme)

    def apply_theme(self, theme_name):
        """Sets the theme styles for the entire interface."""
        theme = self.config.THEMES[theme_name]
        self.setStyleSheet(f""
            f"background-color: {theme['window_bg']};"
            f"color: {theme['user_text_color']};"
            f"font-size: 14px;"
        )
        self.chat_display.setStyleSheet(f"background-color: {theme['chat_bg']}; color: {theme['user_text_color']};")
        self.input_field.setStyleSheet(f"background-color: {theme['input_bg']}; color: {theme['input_text']};")
        self.typing_label.setStyleSheet(f"color: {theme['bot_text_color']};")

    def export_chat(self):
        """Exports the chat history as a plain text file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat", "chat_export.txt", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.chat_display.toPlainText())
                QMessageBox.information(self, "Export Successful", f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def export_chat_json(self):
        """Exports the chat history in structured JSON format."""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat (JSON)", "chat_export.json", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation_log, f, indent=4)
                QMessageBox.information(self, "Export Successful", f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))
