# admin/tabs/chat_tester_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QListWidget, QSplitter,
    QLabel, QMessageBox, QMenu, QComboBox, QCheckBox,
    QFileDialog, QDialog, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from datetime import datetime
import json
import os
import subprocess
import sys

class ChatTesterTab(QWidget):
    """A comprehensive chat testing interface for the admin panel.

    This tab provides a full-featured chat UI for interacting with the chatbot,
    managing chat sessions, switching models, and exporting conversations.
    """
    def contextMenuEvent(self, event):
        """Overrides the default context menu event to show a custom menu.

        Args:
            event (QContextMenuEvent): The context menu event.
        """
        menu = QMenu(self)
        menu.addAction("Copy")
        menu.addAction("Paste")
        menu.addAction("Clear Chat")
        action = menu.exec(event.globalPos())
        if action and action.text() == "Copy":
            if self.chat_display.hasFocus():
                self.chat_display.copy()
            elif self.input_field.hasFocus():
                self.input_field.copy()
        elif action and action.text() == "Paste":
            if self.input_field.hasFocus():
                self.input_field.paste()
        elif action and action.text() == "Clear Chat":
            self.chat_display.clear()

    def setup_context_menus(self):
        """Sets up custom context menus for various widgets."""
        self.chat_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_display.customContextMenuRequested.connect(self.show_chat_context_menu)
        self.input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.input_field.customContextMenuRequested.connect(self.show_input_context_menu)
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_session_context_menu)

    def show_chat_context_menu(self, pos):
        """Shows a context menu for the chat display area.

        Args:
            pos (QPoint): The position where the context menu was requested.
        """
        menu = QMenu(self)
        menu.addAction("Copy")
        menu.addAction("Clear Chat")
        action = menu.exec(self.chat_display.mapToGlobal(pos))
        if action and action.text() == "Copy":
            self.chat_display.copy()
        elif action and action.text() == "Clear Chat":
            self.chat_display.clear()

    def show_input_context_menu(self, pos):
        """Shows a context menu for the message input field.

        Args:
            pos (QPoint): The position where the context menu was requested.
        """
        menu = QMenu(self)
        menu.addAction("Copy")
        menu.addAction("Paste")
        action = menu.exec(self.input_field.mapToGlobal(pos))
        if action and action.text() == "Copy":
            self.input_field.copy()
        elif action and action.text() == "Paste":
            self.input_field.paste()

    def show_session_context_menu(self, pos):
        """Shows a context menu for the session list.

        Args:
            pos (QPoint): The position where the context menu was requested.
        """
        menu = QMenu(self)
        menu.addAction("Delete Session")
        action = menu.exec(self.session_list.mapToGlobal(pos))
        if action and action.text() == "Delete Session":
            self.delete_selected_session()
    def __init__(self, app_instance):
        """Initializes the Chat Tester tab.

        Args:
            app_instance (ChatbotApp): The main application instance.
        """
        super().__init__()
        self.app_instance = app_instance
        self.config = app_instance.config
        self.conversation_log = []
        self.current_theme = "light"
        self.init_ui()

    def init_ui(self):
        """Initializes the UI components of the tab."""
        main_layout = QHBoxLayout(self)

        # Main splitter
        main_splitter = QSplitter()
        main_layout.addWidget(main_splitter)

        # Sidebar
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.addWidget(QLabel("Sessions"))

        toolbar_layout = QHBoxLayout()
        self.session_new_btn = QPushButton("New")
        self.session_refresh_btn = QPushButton("Refresh")
        self.session_delete_btn = QPushButton("Delete")

        toolbar_layout.addWidget(self.session_new_btn)
        toolbar_layout.addWidget(self.session_refresh_btn)
        toolbar_layout.addWidget(self.session_delete_btn)

        self.session_list = QListWidget()

        sidebar_layout.addLayout(toolbar_layout)
        sidebar_layout.addWidget(self.session_list)

        main_splitter.addWidget(sidebar_widget)

        # Chat area
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)

        # Toolbar
        toolbar = QHBoxLayout()
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["svm", "bert"])
        self.model_dropdown.setCurrentText(self.config.MODEL_TYPE)
        self.theme_toggle = QCheckBox("Dark Mode")
        self.retrain_button = QPushButton("Retrain Model")
        self.export_button = QPushButton("Export Chat")
        self.generate_api_key_button = QPushButton("Generate API Key")
        self.profile_button = QPushButton("Profile")

        toolbar.addWidget(QLabel("Model:"))
        toolbar.addWidget(self.model_dropdown)
        toolbar.addWidget(self.theme_toggle)
        toolbar.addWidget(self.retrain_button)
        toolbar.addWidget(self.export_button)
        toolbar.addWidget(self.generate_api_key_button)
        toolbar.addStretch()
        toolbar.addWidget(self.profile_button)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        self.confirmation_buttons_layout = QHBoxLayout()

        chat_layout.addLayout(toolbar)
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(input_layout)
        chat_layout.addLayout(self.confirmation_buttons_layout)

    def clear_confirmation_buttons(self):
        """Removes all widgets from the confirmation buttons layout."""
        while self.confirmation_buttons_layout.count():
            item = self.confirmation_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        main_splitter.addWidget(chat_area)
        main_splitter.setStretchFactor(1, 1)

        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.session_new_btn.clicked.connect(self.create_new_session)
        self.session_refresh_btn.clicked.connect(self.refresh_sessions_sidebar)
        self.session_delete_btn.clicked.connect(self.delete_selected_session)
        self.session_list.itemClicked.connect(self.on_session_selected)

        self.model_dropdown.currentTextChanged.connect(self.switch_model)
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        self.retrain_button.clicked.connect(lambda: self.app_instance.retrain_model())
        self.export_button.clicked.connect(self.export_chat)
        self.profile_button.clicked.connect(self.show_profile_dialog)
        self.generate_api_key_button.clicked.connect(self.generate_api_key)

        self.refresh_sessions_sidebar()
        self.setup_context_menus()

    def send_message(self, text=None):
        """Sends a message to the chatbot and displays the response.

        This method handles both user-typed messages and programmatic
        messages (like 'yes'/'no' for confirmations).

        Args:
            text (str, optional): The text to send. If None, the text from
                the input field is used.
        """
        user_input = text if text is not None else self.input_field.text().strip()
        if not user_input:
            return

        if text is None:
            self.display_message("User", user_input)
            self.input_field.clear()

        self.clear_confirmation_buttons()

        # For the admin panel, we can use a fixed user_id
        admin_user_id = "admin_user"
        response_data = self.app_instance.process_input(admin_user_id, user_input)

        response = response_data.get("response", "Sorry, something went wrong.")
        confidence = response_data.get("confidence", 0.0)
        intent = response_data.get("intent", "unknown")

        self.display_message("Bot", response)

        if intent == "unknown_google_confirm":
            self.show_google_search_confirmation()
        elif intent not in ["google_search", "default"]:
            response_with_confidence = f" (Intent: {intent}, Confidence: {confidence:.2%})"
            self.display_message("Bot", response_with_confidence)

    def show_google_search_confirmation(self):
        """Displays 'Yes' and 'No' buttons for Google Search confirmation."""
        self.clear_confirmation_buttons()

        yes_button = QPushButton("Yes, search Google")
        no_button = QPushButton("No, thank you")

        yes_button.clicked.connect(self.handle_google_search_yes)
        no_button.clicked.connect(self.handle_google_search_no)

        self.confirmation_buttons_layout.addWidget(yes_button)
        self.confirmation_buttons_layout.addWidget(no_button)

    def handle_google_search_yes(self):
        """Handles the 'Yes' click for Google Search confirmation."""
        self.send_message(text="yes")

    def handle_google_search_no(self):
        """Handles the 'No' click for Google Search confirmation."""
        self.send_message(text="no")

    def display_message(self, sender, message):
        """Displays a message in the chat window.

        Args:
            sender (str): The sender of the message (e.g., "User", "Bot").
            message (str): The content of the message.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
        self.conversation_log.append({"time": timestamp, "sender": sender, "text": message})
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def clear_chat(self):
        """Clears the chat display and the conversation log."""
        self.chat_display.clear()
        self.conversation_log.clear()

    def refresh_sessions_sidebar(self):
        """Reloads the list of saved chat sessions in the sidebar."""
        self.session_list.clear()
        try:
            sessions = self.app_instance.list_sessions()
            for s in sessions:
                self.session_list.addItem(s)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sessions: {e}")

    def on_session_selected(self, item):
        """Handles the selection of a session from the list.

        Args:
            item (QListWidgetItem): The selected list item.
        """
        session_name = item.text()
        self.app_instance.load_history(session_name=session_name)

    def create_new_session(self):
        """Creates and saves a new, empty chat session."""
        session_name = datetime.now().strftime('session_%Y%m%d_%H%M%S.json')
        self.app_instance.save_history(session_name=session_name)
        self.refresh_sessions_sidebar()
        self.app_instance.load_history(session_name=session_name)

    def delete_selected_session(self):
        """Deletes the currently selected chat session from disk."""
        item = self.session_list.currentItem()
        if not item:
            return
        name = item.text()
        reply = QMessageBox.question(self, "Delete Session", f"Delete '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                path = os.path.join(self.app_instance.get_sessions_dir(), name)
                if os.path.isfile(path):
                    os.remove(path)
                self.refresh_sessions_sidebar()
            except Exception as e:
                QMessageBox.critical(self, "Delete Session", str(e))

    def switch_model(self, new_model):
        """Switches the active intent classification model.

        Args:
            new_model (str): The name of the model to switch to ('svm' or 'bert').
        """
        import threading
        if new_model != self.config.MODEL_TYPE:
            reply = QMessageBox.question(
                self, "Switch Model",
                f"Switch model to '{new_model}'? This will load the model without retraining.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.config.MODEL_TYPE = new_model
                self.display_message("Bot", f"Loading '{new_model}' model. Please wait...")
                def load_model_thread():
                    loaded = self.app_instance.intent_classifier.load_model()
                    if loaded:
                        self.display_message("Bot", f"Switched to '{new_model}' model and loaded existing weights.")
                    else:
                        self.display_message("Bot", f"Model files for '{new_model}' not found. Please retrain manually.")
                threading.Thread(target=load_model_thread, daemon=True).start()

    def toggle_theme(self):
        """Toggles the UI theme between light and dark mode."""
        self.current_theme = "dark" if self.theme_toggle.isChecked() else "light"
        self.apply_theme()

    def apply_theme(self):
        """Applies the currently selected theme to the UI."""
        theme = self.config.THEMES[self.current_theme]
        self.setStyleSheet(f"background-color: {theme['window_bg']}; color: {theme['user_text_color']};")
        self.chat_display.setStyleSheet(f"background-color: {theme['chat_bg']}; color: {theme['user_text_color']};")
        self.input_field.setStyleSheet(f"background-color: {theme['input_bg']}; color: {theme['input_text']};")

    def export_chat(self):
        """Shows a menu to choose the format for exporting the chat."""
        menu = QMenu(self)
        txt_action = menu.addAction("Export as .txt")
        json_action = menu.addAction("Export as .json")

        action = menu.exec(self.export_button.mapToGlobal(self.export_button.rect().bottomLeft()))

        if action == txt_action:
            self.export_chat_txt()
        elif action == json_action:
            self.export_chat_json()

    def export_chat_txt(self):
        """Exports the current chat conversation to a text file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat", "chat_export.txt", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.chat_display.toPlainText())
                QMessageBox.information(self, "Export Successful", f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def export_chat_json(self):
        """Exports the current chat conversation to a JSON file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat (JSON)", "chat_export.json", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation_log, f, indent=4)
                QMessageBox.information(self, "Export Successful", f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def show_profile_dialog(self):
        """Displays a simple, static user profile dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("User Profile")
        layout = QVBoxLayout(dialog)

        avatar_label = QLabel()
        # You can replace this with a path to a real default avatar image
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.gray)
        avatar_label.setPixmap(pixmap)

        username_label = QLabel("<b>Username:</b> Admin")
        email_label = QLabel("<b>Email:</b> admin@example.com")

        layout.addWidget(avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(username_label)
        layout.addWidget(email_label)

        dialog.exec()

    def generate_api_key(self):
        """Handles the 'Generate API Key' button click event."""
        user_id, ok = QInputDialog.getText(self, "Generate API Key", "Enter User ID:")
        if ok and user_id:
            try:
                new_key = self.app_instance.api_key_manager.generate_api_key(user_id)
                QMessageBox.information(self, "API Key Generated", f"New API Key for {user_id}:\n\n{new_key}\n\nPlease save this key, it will not be shown again.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate API key: {e}")
