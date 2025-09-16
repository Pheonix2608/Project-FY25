# admin/panel.py

"""
This module defines the AdminPanel class which provides the graphical user interface
for administering the chatbot.
"""

import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QComboBox, QFileDialog, QMessageBox, QApplication,
    QListWidget, QSplitter, QCheckBox, QDialog, QInputDialog,
    QTabWidget, QListWidgetItem, QDialogButtonBox, QFormLayout, QSpinBox, QMenu,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import subprocess
import os

class AdminPanel(QWidget):
    """Admin Panel GUI for the chatbot application."""

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
        self.conversation_log = []

        self.setGeometry(100, 100, 1000, 800) # Increased size for admin panel
        self.init_ui()
        self.apply_theme(self.current_theme)

    def init_ui(self):
        """Initializes all UI components and layouts."""
        self.setStyleSheet("font-size: 14px;")

        # Main layout
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_chat_tester_tab()
        self.create_api_key_management_tab()
        self.create_api_session_viewer_tab()

        self.setLayout(layout)

    def create_chat_tester_tab(self):
        """Creates the Chat Tester tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Input area
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.tabs.addTab(tab, "Chat Tester")

    def create_api_key_management_tab(self):
        """Creates the API Key Management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Table for API keys
        self.api_keys_table = QTableWidget()
        self.api_keys_table.setColumnCount(4)
        self.api_keys_table.setHorizontalHeaderLabels(["User ID", "Created At", "Expires At", "Rate Limits"])
        self.api_keys_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.api_keys_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.api_keys_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Buttons
        btn_layout = QHBoxLayout()
        self.generate_key_button = QPushButton("Generate Key")
        self.modify_key_button = QPushButton("Modify User ID")
        self.delete_key_button = QPushButton("Delete Key")
        self.refresh_keys_button = QPushButton("Refresh")

        btn_layout.addWidget(self.generate_key_button)
        btn_layout.addWidget(self.modify_key_button)
        btn_layout.addWidget(self.delete_key_button)
        btn_layout.addWidget(self.refresh_keys_button)

        layout.addWidget(self.api_keys_table)
        layout.addLayout(btn_layout)

        # Connect signals
        self.generate_key_button.clicked.connect(self.generate_api_key)
        self.modify_key_button.clicked.connect(self.modify_api_key)
        self.delete_key_button.clicked.connect(self.delete_api_key)
        self.refresh_keys_button.clicked.connect(self.refresh_api_keys_tab)

        self.tabs.addTab(tab, "API Key Management")

        # Initial load
        self.refresh_api_keys_tab()

    def create_api_session_viewer_tab(self):
        """Creates the API Session Viewer tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by User ID:"))
        self.session_filter_input = QLineEdit()
        self.session_filter_input.textChanged.connect(self.refresh_api_sessions_tab)
        filter_layout.addWidget(self.session_filter_input)

        # Table for sessions
        self.api_sessions_table = QTableWidget()
        self.api_sessions_table.setColumnCount(5)
        self.api_sessions_table.setHorizontalHeaderLabels(["Timestamp", "User ID", "Message", "Response", "Intent"])
        self.api_sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Refresh button
        self.refresh_sessions_button = QPushButton("Refresh")
        self.refresh_sessions_button.clicked.connect(self.refresh_api_sessions_tab)

        layout.addLayout(filter_layout)
        layout.addWidget(self.api_sessions_table)
        layout.addWidget(self.refresh_sessions_button)

        self.tabs.addTab(tab, "API Session Viewer")

        # Initial load
        self.refresh_api_sessions_tab()

    # --- Chat Tester Methods ---
    def send_message(self):
        """Handles user input and triggers bot response in the chat tester."""
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.display_message("User", user_input)
        self.input_field.clear()

        response_data = self.app_instance.process_input(user_input)
        response = response_data.get("response", "Sorry, something went wrong.")
        confidence = response_data.get("confidence", 0.0)
        intent = response_data.get("intent", "unknown")

        response_with_confidence = f"{response} (Intent: {intent}, Confidence: {confidence:.2%})"
        self.display_message("Bot", response_with_confidence)

    def display_message(self, sender, message):
        """Displays a message in the chat window with a timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
        self.conversation_log.append({"time": timestamp, "sender": sender, "text": message})
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    # --- API Key Management Methods ---
    def refresh_api_keys_tab(self):
        """Loads and displays all API keys."""
        try:
            keys = self.app_instance.api_key_manager.list_all_api_keys()
            self.api_keys_table.setRowCount(0)
            for user_id, data in keys.items():
                row_position = self.api_keys_table.rowCount()
                self.api_keys_table.insertRow(row_position)
                self.api_keys_table.setItem(row_position, 0, QTableWidgetItem(user_id))
                self.api_keys_table.setItem(row_position, 1, QTableWidgetItem(data.get("created_at")))
                self.api_keys_table.setItem(row_position, 2, QTableWidgetItem(data.get("expires_at")))
                self.api_keys_table.setItem(row_position, 3, QTableWidgetItem(str(data.get("rate_limit"))))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load API keys: {e}")

    def generate_api_key(self):
        """Generates a new API key."""
        user_id, ok = QInputDialog.getText(self, "Generate API Key", "Enter User ID:")
        if ok and user_id:
            try:
                new_key = self.app_instance.api_key_manager.generate_api_key(user_id)
                QMessageBox.information(self, "API Key Generated", f"New API Key for {user_id}:\n\n{new_key}\n\nPlease save this key, it will not be shown again.")
                self.refresh_api_keys_tab()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate API key: {e}")

    def modify_api_key(self):
        """Modifies the user ID of a selected API key."""
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an API key to modify.")
            return

        selected_row = selected_rows[0].row()
        old_user_id = self.api_keys_table.item(selected_row, 0).text()

        new_user_id, ok = QInputDialog.getText(self, "Modify User ID", f"Enter new User ID for '{old_user_id}':")
        if ok and new_user_id:
            try:
                success = self.app_instance.api_key_manager.modify_api_key_user(old_user_id, new_user_id)
                if success:
                    QMessageBox.information(self, "Success", f"User ID for key has been changed to {new_user_id}.")
                    self.refresh_api_keys_tab()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to modify User ID. The new User ID might already exist.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to modify API key: {e}")

    def delete_api_key(self):
        """Deletes a selected API key."""
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an API key to delete.")
            return

        selected_row = selected_rows[0].row()
        user_id = self.api_keys_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "Delete API Key", f"Are you sure you want to delete the API key for '{user_id}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.app_instance.api_key_manager.delete_api_key(user_id)
                if success:
                    QMessageBox.information(self, "Success", f"API key for {user_id} has been deleted.")
                    self.refresh_api_keys_tab()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to delete API key.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete API key: {e}")

    # --- API Session Viewer Methods ---
    def refresh_api_sessions_tab(self):
        """Loads and displays all API sessions, with optional filtering."""
        try:
            log_file = os.path.join(self.config.BASE_DIR, 'data', 'api_sessions.json')
            if not os.path.exists(log_file):
                self.api_sessions_table.setRowCount(0)
                return

            with open(log_file, 'r') as f:
                logs = json.load(f)

            filter_text = self.session_filter_input.text().strip().lower()

            self.api_sessions_table.setRowCount(0)
            for log in logs:
                if filter_text and filter_text not in log.get("user_id", "").lower():
                    continue

                row_position = self.api_sessions_table.rowCount()
                self.api_sessions_table.insertRow(row_position)
                self.api_sessions_table.setItem(row_position, 0, QTableWidgetItem(log.get("timestamp")))
                self.api_sessions_table.setItem(row_position, 1, QTableWidgetItem(log.get("user_id")))
                self.api_sessions_table.setItem(row_position, 2, QTableWidgetItem(log.get("message")))
                self.api_sessions_table.setItem(row_position, 3, QTableWidgetItem(log.get("response")))
                self.api_sessions_table.setItem(row_position, 4, QTableWidgetItem(log.get("intent")))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load API sessions: {e}")


    def apply_theme(self, theme_name):
        """Sets the theme styles for the entire interface."""
        # This can be simplified or removed if the admin panel doesn't need themes
        pass
