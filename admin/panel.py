# admin/panel.py

"""
This module defines the main AdminPanel class that brings all the admin tabs together.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from admin.tabs.chat_tester_tab import ChatTesterTab
from admin.tabs.api_key_management_tab import ApiKeyManagementTab
from admin.tabs.api_session_viewer_tab import ApiSessionViewerTab
from admin.tabs.settings_tab import SettingsTab

class AdminPanel(QWidget):
    def apply_dark_mode(self, enabled):
        if enabled:
            # Simple dark theme stylesheet
            self.setStyleSheet("""
                QWidget { background-color: #232629; color: #f3f3f3; }
                QTabWidget::pane { border: 1px solid #444; }
                QTabBar::tab { background: #333; color: #f3f3f3; border: 1px solid #444; padding: 8px; }
                QTabBar::tab:selected { background: #232629; }
                QPushButton { background-color: #444; color: #f3f3f3; border: 1px solid #666; }
                QCheckBox { color: #f3f3f3; }
                QLabel { color: #f3f3f3; }
            """)
        else:
            self.setStyleSheet("")
    """Admin Panel GUI for the chatbot application."""

    def __init__(self, app):
        """
        Initialize the GUI and build the tabbed layout.

        Args:
            app (ChatbotApp): The main application instance.
        """
        super().__init__()
        self.app_instance = app
        self.config = app.config

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle(f"{self.config.PROJECT_NAME} v{self.config.VERSION} - Admin Panel")
        self.init_ui()

    def init_ui(self):
        """Initializes all UI components and layouts."""
        self.setStyleSheet("font-size: 14px;")

        # Main layout
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create and add tabs
        self.chat_tester_tab = ChatTesterTab(self.app_instance)
        self.api_key_management_tab = ApiKeyManagementTab(self.app_instance)
        self.api_session_viewer_tab = ApiSessionViewerTab()
        self.settings_tab = SettingsTab(self.app_instance)

        self.tabs.addTab(self.chat_tester_tab, "Chat Tester")
        self.tabs.addTab(self.api_key_management_tab, "API Key Management")
        self.tabs.addTab(self.api_session_viewer_tab, "API Session Viewer")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.setLayout(layout)

    def display_message(self, sender, message):
        """Delegate method to display a message in the chat tester tab."""
        self.chat_tester_tab.display_message(sender, message)

    def clear_chat(self):
        """Delegate method to clear the chat in the chat tester tab."""
        self.chat_tester_tab.clear_chat()
