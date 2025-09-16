# admin/tabs/settings_tab.py

from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QPushButton,
    QLabel, QCheckBox
)
from PyQt6.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.config = app_instance.config
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Retrain buttons
        self.retrain_button = QPushButton("Retrain Model (Blocking)")
        self.retrain_button.clicked.connect(lambda: self.app_instance.retrain_model(background=False))

        self.retrain_bg_button = QPushButton("Retrain Model (Background)")
        self.retrain_bg_button.clicked.connect(lambda: self.app_instance.retrain_model(background=True))

        layout.addRow(QLabel("Model Training:"), self.retrain_button)
        layout.addRow(None, self.retrain_bg_button)

        # Google Search toggle
        self.google_search_toggle = QCheckBox("Enable Google Search Fallback")
        self.google_search_toggle.setChecked(self.config.ENABLE_GOOGLE_FALLBACK)
        self.google_search_toggle.stateChanged.connect(self.toggle_google_search)

        layout.addRow(QLabel("Features:"), self.google_search_toggle)

        self.setLayout(layout)

    def toggle_google_search(self, state):
        is_enabled = state == Qt.CheckState.Checked.value
        self.config.ENABLE_GOOGLE_FALLBACK = is_enabled
        # We can show a message box, but it might be annoying.
        # A status bar message would be better in a real app.
        print(f"Google Search fallback has been {'enabled' if is_enabled else 'disabled'}.")
