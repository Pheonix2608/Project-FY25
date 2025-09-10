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
    QLineEdit, QLabel, QComboBox, QFileDialog, QMessageBox, QApplication,
    QListWidget, QSplitter, QCheckBox, QDialog, QInputDialog,
    QTabWidget, QListWidgetItem, QDialogButtonBox, QFormLayout, QSpinBox, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QIcon
import subprocess
import os
# Removed animated toggle; will use a simple checkbox for theme switching.

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
        # Icon placeholders from data/images
        base_images = os.path.join(self.config.BASE_DIR, 'data', 'images')
        self.icons = {
            'bot': os.path.join(base_images, 'bot.png'),
            'user': os.path.join(base_images, 'user.png'),
            'settings': os.path.join(base_images, 'settings.png'),
            'new': os.path.join(base_images, 'new.png'),
            'refresh': os.path.join(base_images, 'refresh.png'),
            'delete': os.path.join(base_images, 'delete.png'),
            'folder': os.path.join(base_images, 'folder.png')
        }

        self.setGeometry(100, 100, self.config.GUI_WIDTH, self.config.GUI_HEIGHT)
        self.init_ui()
        self.apply_theme(self.current_theme)


    def init_ui(self):
        """Initializes all UI components and layouts, including sidebar tabs and theme toggle."""
       
        self.setStyleSheet("font-size: 14px;")

        # Sidebar: Sessions list plus Settings button
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.on_session_selected)
        self.refresh_sessions_sidebar()
        # Context menu for sessions
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.on_sessions_context_menu)

        self.settings_button = QPushButton("Settings")
        # Try to set placeholder icon if present
        try:
            if os.path.isfile(self.icons['settings']):
                self.settings_button.setIcon(QIcon(self.icons['settings']))
        except Exception:
            pass
        self.settings_button.clicked.connect(self.open_settings_dialog)

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
        self.save_button.clicked.connect(lambda: self.app_instance.save_history())
        self.load_button = QPushButton("Load Latest")
        self.load_button.clicked.connect(lambda: self.app_instance.load_history())
        self.export_button = QPushButton("Export Chat")
        self.export_button.clicked.connect(self.export_chat)
        self.export_json_button = QPushButton("Export JSON")
        self.export_json_button.clicked.connect(self.export_chat_json)
        self.retrain_button = QPushButton("Retrain Model")
        self.retrain_button.clicked.connect(self.app_instance.retrain_model)
        self.generate_key_button = QPushButton("Generate API Key")
        self.generate_key_button.clicked.connect(self.on_generate_api_key)
        
        # Typing indicator
        self.typing_label = QLabel("")
        
        # Dropdown for model selection
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["svm", "bert"])
        self.model_dropdown.setCurrentText(self.config.MODEL_TYPE)
        self.model_dropdown.currentTextChanged.connect(self.switch_model)
        
        # Simple theme toggle
        self.theme_toggle = QCheckBox("Dark mode")
        self.theme_toggle.setChecked(self.current_theme == "dark")
        self.theme_toggle.stateChanged.connect(self.toggle_theme)

        # Layouts
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.send_button)
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.export_button)
        btn_layout.addWidget(self.export_json_button)
        btn_layout.addWidget(self.retrain_button)
        btn_layout.addWidget(self.generate_key_button)

        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Model:"))
        settings_layout.addWidget(self.model_dropdown)
        settings_layout.addWidget(self.theme_toggle)
        settings_layout.addStretch()

        # Main layout with sidebar (sessions + settings)
        main_splitter = QSplitter()
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(QLabel("Sessions"))
        # Toolbar under Sessions label
        toolbar_layout = QHBoxLayout()
        self.session_new_btn = QPushButton("")
        self.session_refresh_btn = QPushButton("")
        self.session_delete_btn = QPushButton("")
        self.session_folder_btn = QPushButton("")
        # Set icons if placeholders exist
        try:
            if os.path.isfile(self.icons['new']):
                self.session_new_btn.setIcon(QIcon(self.icons['new']))
            else:
                self.session_new_btn.setText("New")
            if os.path.isfile(self.icons['refresh']):
                self.session_refresh_btn.setIcon(QIcon(self.icons['refresh']))
            else:
                self.session_refresh_btn.setText("Refresh")
            if os.path.isfile(self.icons['delete']):
                self.session_delete_btn.setIcon(QIcon(self.icons['delete']))
            else:
                self.session_delete_btn.setText("Delete")
            if os.path.isfile(self.icons['folder']):
                self.session_folder_btn.setIcon(QIcon(self.icons['folder']))
            else:
                self.session_folder_btn.setText("Open")
        except Exception:
            self.session_new_btn.setText("New")
            self.session_refresh_btn.setText("Refresh")
            self.session_delete_btn.setText("Delete")
            self.session_folder_btn.setText("Open")
        # Wire actions
        self.session_new_btn.clicked.connect(self.create_new_session)
        self.session_refresh_btn.clicked.connect(self.refresh_sessions_sidebar)
        self.session_delete_btn.clicked.connect(self.delete_selected_session)
        self.session_folder_btn.clicked.connect(self.open_sessions_folder)
        # Compact styling
        for b in [self.session_new_btn, self.session_refresh_btn, self.session_delete_btn, self.session_folder_btn]:
            b.setFixedHeight(28)
        toolbar_layout.addWidget(self.session_new_btn)
        toolbar_layout.addWidget(self.session_refresh_btn)
        toolbar_layout.addWidget(self.session_delete_btn)
        toolbar_layout.addWidget(self.session_folder_btn)
        sidebar_layout.addLayout(toolbar_layout)
        sidebar_layout.addWidget(self.session_list)
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addStretch()
        sidebar_widget.setLayout(sidebar_layout)
        main_splitter.addWidget(sidebar_widget)

        chat_area = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.addLayout(settings_layout)
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.typing_label)
        chat_layout.addWidget(self.input_field)
        chat_layout.addLayout(btn_layout)
        chat_area.setLayout(chat_layout)

        main_splitter.addWidget(chat_area)
        main_splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)


    def toggle_theme(self):
        """Toggle between light and dark themes using a simple checkbox."""
        new_theme = "dark" if self.theme_toggle.isChecked() else "light"
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme(new_theme)

    def refresh_sessions_sidebar(self):
        """Refresh the session list sidebar with available session files."""
        self.session_list.clear()
        try:
            sessions = self.app_instance.list_sessions()
            for s in sessions:
                self.session_list.addItem(s)
        except Exception:
            pass

    def refresh_images_sidebar(self):
        """Refresh the images tab listing files in data/images."""
        self.image_list.clear()
        try:
            images_dir = os.path.join(self.app_instance.config.BASE_DIR, 'data', 'images')
            if os.path.isdir(images_dir):
                files = sorted([f for f in os.listdir(images_dir) if not f.startswith('.')])
                for f in files:
                    self.image_list.addItem(QListWidgetItem(f))
        except Exception:
            pass

    def on_session_selected(self, item):
        """Load the selected session when clicked in the sidebar."""
        session_name = item.text()
        self.app_instance.load_history(session_name=session_name)

    def on_sessions_context_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("New Session", self.create_new_session)
        menu.addAction("Refresh", self.refresh_sessions_sidebar)
        if self.session_list.currentItem():
            menu.addAction("Load", lambda: self.on_session_selected(self.session_list.currentItem()))
            menu.addAction("Delete", self.delete_selected_session)
        menu.addAction("Open Folder", self.open_sessions_folder)
        menu.exec(self.session_list.mapToGlobal(pos))

    def create_new_session(self):
        # Create an empty session file with timestamp
        try:
            name = datetime.now().strftime('session_%Y%m%d_%H%M%S.json')
            sessions_dir = self.app_instance.get_sessions_dir()
            path = os.path.join(sessions_dir, name)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.refresh_sessions_sidebar()
            self.app_instance.load_history(session_name=name)
        except Exception as e:
            QMessageBox.critical(self, "New Session", str(e))

    def delete_selected_session(self):
        try:
            item = self.session_list.currentItem()
            if not item:
                return
            name = item.text()
            reply = QMessageBox.question(self, "Delete Session", f"Delete '{name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
            path = os.path.join(self.app_instance.get_sessions_dir(), name)
            if os.path.isfile(path):
                os.remove(path)
            self.refresh_sessions_sidebar()
        except Exception as e:
            QMessageBox.critical(self, "Delete Session", str(e))

    def open_sessions_folder(self):
        try:
            folder = self.app_instance.get_sessions_dir()
            if sys.platform.startswith('win'):
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            QMessageBox.critical(self, "Open Folder", str(e))

    def display_message(self, sender, message):
        """Displays a message in the chat window with a timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
        self.conversation_log.append({"time": timestamp, "sender": sender, "text": message})

    # Removed image selection handler since Images tab was removed

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
        self.setStyleSheet(
            f"background-color: {theme['window_bg']};"
            f"color: {theme['user_text_color']};"
            f"font-size: 14px;"
            # Tabs styling to keep labels visible in dark mode
            f" QTabWidget::pane {{ border: 1px solid {theme.get('border_color', '#444')}; }}"
            f" QTabBar::tab {{ color: {theme['user_text_color']}; background: {theme['chat_bg']}; padding: 6px 10px; border: 1px solid {theme.get('border_color', '#444')}; border-bottom: none; }}"
            f" QTabBar::tab:selected {{ background: {theme.get('user_bubble_bg', theme['chat_bg'])}; }}"
            f" QTabBar::tab:!selected {{ background: {theme['chat_bg']}; }}"
        )
        self.chat_display.setStyleSheet(f"background-color: {theme['chat_bg']}; color: {theme['user_text_color']};")
        self.input_field.setStyleSheet(f"background-color: {theme['input_bg']}; color: {theme['input_text']};")
        self.typing_label.setStyleSheet(f"color: {theme['bot_text_color']};")
        # Reset button styles (inherit from OS/theme)
        for btn in [self.send_button, self.save_button, self.load_button, self.export_button,
                    self.export_json_button, self.retrain_button, self.generate_key_button, self.settings_button]:
            btn.setStyleSheet("")

    def open_settings_dialog(self):
        """Open a modular settings dialog with tabs and placeholders."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")

        tabs = QTabWidget()
        # Ensure tab labels are visible under current theme
        theme = self.config.THEMES.get(self.current_theme, self.config.THEMES['light'])
        tabs.setStyleSheet(
            f" QTabWidget::pane {{ border: 1px solid {theme.get('border_color', '#444')}; }}"
            f" QTabBar::tab {{ color: {theme.get('user_text_color', '#000')};"
            f" background: {theme.get('chat_bg', '#fff')}; padding: 6px 10px;"
            f" border: 1px solid {theme.get('border_color', '#444')}; border-bottom: none; }}"
            f" QTabBar::tab:selected {{ background: {theme.get('user_bubble_bg', theme.get('chat_bg', '#fff'))};"
            f" color: {theme.get('user_text_color', '#000')}; }}"
            f" QTabBar::tab:!selected {{ background: {theme.get('chat_bg', '#fff')}; }}"
        )

        # General tab
        general_tab = QWidget()
        general_form = QFormLayout()
        theme_select = QComboBox()
        theme_select.addItems(list(self.config.THEMES.keys()))
        theme_select.setCurrentText(self.current_theme)
        model_select = QComboBox()
        model_select.addItems(["svm", "bert"])
        model_select.setCurrentText(self.config.MODEL_TYPE)
        context_spin = QSpinBox()
        context_spin.setRange(1, 20)
        context_spin.setValue(self.app_instance.config.CONTEXT_WINDOW_SIZE)
        general_form.addRow("Theme", theme_select)
        general_form.addRow("Model", model_select)
        general_form.addRow("Context Window", context_spin)
        general_tab.setLayout(general_form)
        tabs.addTab(general_tab, "General")

        # API tab
        api_tab = QWidget()
        api_form = QFormLayout()
        api_host = QLineEdit()
        api_port = QLineEdit()
        api_host.setText(str(getattr(self.app_instance.config, 'API_HOST', '0.0.0.0')))
        api_port.setText(str(getattr(self.app_instance.config, 'API_PORT', 8080)))
        api_form.addRow("API Host", api_host)
        api_form.addRow("API Port", api_port)
        api_tab.setLayout(api_form)
        tabs.addTab(api_tab, "API")

        # Data tab (placeholders)
        data_tab = QWidget()
        data_form = QFormLayout()
        intents_dir = QLineEdit()
        intents_dir.setText(getattr(self.app_instance.config, 'INTENTS_DIR', ''))
        images_dir = QLineEdit()
        images_dir.setText(os.path.join(self.app_instance.config.BASE_DIR, 'data', 'images'))
        data_form.addRow("Intents Directory", intents_dir)
        data_form.addRow("Images Directory", images_dir)
        data_tab.setLayout(data_form)
        tabs.addTab(data_tab, "Data")

        # About tab (placeholder)
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        about_layout.addWidget(QLabel("Chatbot UI v1.0\nThis is a placeholder About section."))
        about_tab.setLayout(about_layout)
        tabs.addTab(about_tab, "About")

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        def apply_and_close():
            # Apply selected settings
            sel_theme = theme_select.currentText()
            if sel_theme != self.current_theme:
                self.theme_toggle.setChecked(sel_theme == 'dark')
                self.apply_theme(sel_theme)
                self.current_theme = sel_theme

            sel_model = model_select.currentText()
            if sel_model != self.config.MODEL_TYPE:
                self.config.MODEL_TYPE = sel_model
                # Defer retraining; user can click retrain button

            # Context window size
            self.app_instance.config.CONTEXT_WINDOW_SIZE = context_spin.value()

            # API settings
            self.app_instance.config.API_HOST = api_host.text().strip() or self.app_instance.config.API_HOST
            try:
                self.app_instance.config.API_PORT = int(api_port.text().strip())
            except ValueError:
                pass

            dlg.accept()

        buttons.accepted.connect(apply_and_close)
        buttons.rejected.connect(dlg.reject)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        dlg.resize(520, 420)
        dlg.exec()

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

    def on_generate_api_key(self):
        """Generate an API key and show it to the user."""
        try:
            user_id, ok = QInputDialog.getText(self, "User ID", "Enter a user ID for this API key:", text="gui_user")
            if not ok or not user_id.strip():
                return
            api_key = self.app_instance.generate_api_key(user_id=user_id.strip())
            if not api_key:
                QMessageBox.critical(self, "API Key", "Failed to generate API key.")
                return
            self.show_api_key_dialog(api_key)
        except Exception as e:
            QMessageBox.critical(self, "API Key", str(e))

    def show_api_key_dialog(self, api_key: str):
        """Show a dialog with selectable and copyable API key and endpoint."""
        endpoint = f"http://{self.app_instance.config.API_HOST}:{self.app_instance.config.API_PORT}/chat"

        dlg = QDialog(self)
        dlg.setWindowTitle("API Key Generated")

        layout = QVBoxLayout()
        info = QLabel("Your API key (copy now, shown only once):")
        layout.addWidget(info)

        key_input = QLineEdit()
        key_input.setText(api_key)
        key_input.setReadOnly(True)
        key_input.setCursorPosition(0)
        layout.addWidget(key_input)

        key_btns = QHBoxLayout()
        copy_key_btn = QPushButton("Copy Key")
        copy_key_btn.clicked.connect(lambda: QApplication.clipboard().setText(api_key))
        key_btns.addWidget(copy_key_btn)
        layout.addLayout(key_btns)

        ep_label = QLabel("Endpoint (use POST):")
        layout.addWidget(ep_label)

        ep_input = QLineEdit()
        ep_input.setText(endpoint)
        ep_input.setReadOnly(True)
        ep_input.setCursorPosition(0)
        layout.addWidget(ep_input)

        ep_btns = QHBoxLayout()
        copy_ep_btn = QPushButton("Copy Endpoint")
        copy_ep_btn.clicked.connect(lambda: QApplication.clipboard().setText(endpoint))
        ep_btns.addWidget(copy_ep_btn)
        layout.addLayout(ep_btns)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.setLayout(layout)
        dlg.resize(520, 200)
        dlg.exec()
