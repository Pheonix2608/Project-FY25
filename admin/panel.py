# admin/panel.py

"""
This module defines the main AdminPanel class that brings all the admin tabs together.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from admin.tabs.chat_tester_tab import ChatTesterTab
from admin.tabs.api_key_management_tab import ApiKeyManagementTab
from admin.tabs.api_session_viewer_tab import ApiSessionViewerTab
from admin.tabs.settings_tab import SettingsTab
from admin.tabs.system_stats_tab import SystemStatsTab
from admin.tabs.log_viewer_tab import LogViewerTab

class AdminPanel(QWidget):
    """The main Admin Panel GUI for the chatbot application.

    This class serves as the main window for the admin panel, organizing
    various management and testing functionalities into a tabbed interface.
    """
    def apply_dark_mode(self, enabled):
        """Applies or removes a simple dark mode stylesheet.

        Args:
            enabled (bool): If True, the dark mode stylesheet is applied.
                If False, the default stylesheet is restored.
        """
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

    def __init__(self, app):
        """Initializes the AdminPanel GUI and builds the tabbed layout.

        Args:
            app (ChatbotApp): The main application instance, which provides
                access to the chatbot's core functionalities and configuration.
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
        self.system_stats_tab = SystemStatsTab()
        self.log_viewer_tab = LogViewerTab(self.config.LOG_DIR)

        self.tabs.addTab(self.chat_tester_tab, "Chat Tester")
        self.tabs.addTab(self.api_key_management_tab, "API Key Management")
        self.tabs.addTab(self.api_session_viewer_tab, "API Session Viewer")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.system_stats_tab, "System Stats")
        self.tabs.addTab(self.log_viewer_tab, "Log Viewer")

        self.setLayout(layout)

    def display_message(self, sender, message):
        """Delegates displaying a message to the Chat Tester tab.

        Args:
            sender (str): The sender of the message (e.g., "User", "Bot").
            message (str): The content of the message to display.
        """
        self.chat_tester_tab.display_message(sender, message)

    def clear_chat(self):
        """Delegates clearing the chat display to the Chat Tester tab."""
        self.chat_tester_tab.clear_chat()
