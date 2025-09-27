# admin/tabs/settings_tab.py

from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QPushButton,
    QLabel, QCheckBox, QDoubleSpinBox
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

        # Confidence Threshold
        self.confidence_threshold_spinner = QDoubleSpinBox()
        self.confidence_threshold_spinner.setRange(0.0, 1.0)
        self.confidence_threshold_spinner.setSingleStep(0.05)
        self.confidence_threshold_spinner.setValue(self.config.CONFIDENCE_THRESHOLD)
        self.confidence_threshold_spinner.valueChanged.connect(self.update_confidence_threshold)
        layout.addRow(QLabel("Confidence Threshold:"), self.confidence_threshold_spinner)

        # Google Search toggle
        self.google_search_toggle = QCheckBox("Enable Google Search Fallback")
        self.google_search_toggle.setChecked(self.config.ENABLE_GOOGLE_FALLBACK)
        self.google_search_toggle.stateChanged.connect(self.toggle_google_search)

        layout.addRow(QLabel("Features:"), self.google_search_toggle)

        # Dark mode toggle
        self.dark_mode_toggle = QCheckBox("Switch to Dark Mode (UI Theme)")
        self.dark_mode_toggle.setChecked(getattr(self.config, 'DARK_MODE', False))
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        layout.addRow(QLabel("Appearance:"), self.dark_mode_toggle)

        self.setLayout(layout)

    def update_confidence_threshold(self, value):
        """Updates the confidence threshold in the config."""
        self.config.CONFIDENCE_THRESHOLD = value
        print(f"Confidence threshold updated to: {value}")

    def toggle_google_search(self, state):
        is_enabled = state == Qt.CheckState.Checked.value
        self.config.ENABLE_GOOGLE_FALLBACK = is_enabled
        # We can show a message box, but it might be annoying.
        # A status bar message would be better in a real app.
        print(f"Google Search fallback has been {'enabled' if is_enabled else 'disabled'}.")

    def toggle_dark_mode(self, state):
        is_enabled = state == Qt.CheckState.Checked.value
        self.config.DARK_MODE = is_enabled
        # Apply dark mode to the main window
        if hasattr(self.app_instance, 'gui') and self.app_instance.gui:
            self.app_instance.gui.apply_dark_mode(is_enabled)
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Theme Changed")
        msg.setText(f"{'Dark' if is_enabled else 'Light'} mode is now active.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
