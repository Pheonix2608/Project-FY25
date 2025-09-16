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
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.config = app_instance.config
        self.conversation_log = []
        self.current_theme = "light"
        self.init_ui()

    def init_ui(self):
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

        chat_layout.addLayout(toolbar)
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(input_layout)

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

    def send_message(self):
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
        self.conversation_log.append({"time": timestamp, "sender": sender, "text": message})
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def clear_chat(self):
        self.chat_display.clear()
        self.conversation_log.clear()

    def refresh_sessions_sidebar(self):
        self.session_list.clear()
        try:
            sessions = self.app_instance.list_sessions()
            for s in sessions:
                self.session_list.addItem(s)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sessions: {e}")

    def on_session_selected(self, item):
        session_name = item.text()
        self.app_instance.load_history(session_name=session_name)

    def create_new_session(self):
        session_name = datetime.now().strftime('session_%Y%m%d_%H%M%S.json')
        self.app_instance.save_history(session_name=session_name)
        self.refresh_sessions_sidebar()
        self.app_instance.load_history(session_name=session_name)

    def delete_selected_session(self):
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

    def toggle_theme(self):
        self.current_theme = "dark" if self.theme_toggle.isChecked() else "light"
        self.apply_theme()

    def apply_theme(self):
        theme = self.config.THEMES[self.current_theme]
        self.setStyleSheet(f"background-color: {theme['window_bg']}; color: {theme['user_text_color']};")
        self.chat_display.setStyleSheet(f"background-color: {theme['chat_bg']}; color: {theme['user_text_color']};")
        self.input_field.setStyleSheet(f"background-color: {theme['input_bg']}; color: {theme['input_text']};")

    def export_chat(self):
        menu = QMenu(self)
        txt_action = menu.addAction("Export as .txt")
        json_action = menu.addAction("Export as .json")

        action = menu.exec(self.export_button.mapToGlobal(self.export_button.rect().bottomLeft()))

        if action == txt_action:
            self.export_chat_txt()
        elif action == json_action:
            self.export_chat_json()

    def export_chat_txt(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat", "chat_export.txt", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.chat_display.toPlainText())
                QMessageBox.information(self, "Export Successful", f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def export_chat_json(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat (JSON)", "chat_export.json", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation_log, f, indent=4)
                QMessageBox.information(self, "Export Successful", f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def show_profile_dialog(self):
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
        """Generates a new API key."""
        user_id, ok = QInputDialog.getText(self, "Generate API Key", "Enter User ID:")
        if ok and user_id:
            try:
                new_key = self.app_instance.api_key_manager.generate_api_key(user_id)
                QMessageBox.information(self, "API Key Generated", f"New API Key for {user_id}:\n\n{new_key}\n\nPlease save this key, it will not be shown again.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate API key: {e}")
