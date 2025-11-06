# admin/tabs/settings_tab.py

import socket
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QPushButton,
    QLabel, QCheckBox, QDoubleSpinBox,
    QHBoxLayout, QMessageBox, QLineEdit,
    QVBoxLayout, QGroupBox, QSpinBox, QApplication
)


class SettingsTab(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.config = app_instance.config
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Model Settings ---
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout()

        # Retrain buttons
        self.retrain_button = QPushButton("Retrain Model (Blocking)")
        self.retrain_button.clicked.connect(
            lambda: self.app_instance.retrain_model(background=False)
        )

        self.retrain_bg_button = QPushButton("Retrain Model (Background)")
        self.retrain_bg_button.clicked.connect(
            lambda: self.app_instance.retrain_model(background=True)
        )

        model_layout.addRow(QLabel("Model Training:"), self.retrain_button)
        model_layout.addRow(None, self.retrain_bg_button)

        # Confidence threshold control
        threshold_layout = QHBoxLayout()
        self.confidence_threshold = QDoubleSpinBox()
        self.confidence_threshold.setRange(0.0, 1.0)
        self.confidence_threshold.setSingleStep(0.05)
        self.confidence_threshold.setDecimals(2)
        self.confidence_threshold.setValue(self.config.CONFIDENCE_THRESHOLD)
        self.confidence_threshold.valueChanged.connect(
            self.update_confidence_threshold
        )

        threshold_reset = QPushButton("Reset")
        threshold_reset.clicked.connect(
            lambda: self.confidence_threshold.setValue(0.5)
        )

        threshold_layout.addWidget(self.confidence_threshold)
        threshold_layout.addWidget(threshold_reset)
        threshold_layout.addStretch()

        confidence_label = QLabel("Response Confidence Threshold:")
        confidence_label.setToolTip(
            "Minimum confidence level required for the model to use an intent-based response.\n"
            "Values below this threshold will trigger fallback behavior."
        )
        model_layout.addRow(confidence_label, threshold_layout)

        model_group.setLayout(model_layout)
        main_layout.addWidget(model_group)

        # --- API Settings ---
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout()

        # Host
        host_layout = QHBoxLayout()
        self.host_display = QLineEdit(self.get_host_address())
        self.host_display.setReadOnly(True)
        self.host_display.setToolTip("Address to access the chatbot API")
        copy_host_btn = QPushButton("Copy")
        copy_host_btn.clicked.connect(self.copy_host_address)
        host_layout.addWidget(self.host_display)
        host_layout.addWidget(copy_host_btn)
        api_layout.addRow("API Host:", host_layout)

        # Port
        port_layout = QHBoxLayout()
        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1024, 65535)
        self.port_spinbox.setValue(self.config.API_PORT)
        self.port_spinbox.valueChanged.connect(self.update_port)
        port_layout.addWidget(self.port_spinbox)
        port_layout.addStretch()
        api_layout.addRow("API Port:", port_layout)

        # Full URL
        url_layout = QHBoxLayout()
        self.url_display = QLineEdit(self.get_full_url())
        self.url_display.setReadOnly(True)
        copy_url_btn = QPushButton("Copy Full URL")
        copy_url_btn.clicked.connect(self.copy_full_url)
        url_layout.addWidget(self.url_display)
        url_layout.addWidget(copy_url_btn)
        api_layout.addRow("API URL:", url_layout)

        api_group.setLayout(api_layout)
        main_layout.addWidget(api_group)

        # --- Features ---
        features_group = QGroupBox("Features")
        features_layout = QFormLayout()
        self.google_search_toggle = QCheckBox("Enable Google Search Fallback")
        self.google_search_toggle.setChecked(self.config.ENABLE_GOOGLE_FALLBACK)
        self.google_search_toggle.stateChanged.connect(self.toggle_google_search)
        features_layout.addRow(self.google_search_toggle)
        features_group.setLayout(features_layout)
        main_layout.addWidget(features_group)

        # --- Appearance ---
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        self.dark_mode_toggle = QCheckBox("Switch to Dark Mode (UI Theme)")
        self.dark_mode_toggle.setChecked(getattr(self.config, "DARK_MODE", False))
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        appearance_layout.addRow(self.dark_mode_toggle)
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    # -------------------- Logic --------------------

    def get_host_address(self):
        """Gets the host address for API access."""
        if getattr(self.config, "API_HOST", "0.0.0.0") == "0.0.0.0":
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception:
                return "127.0.0.1"
        return self.config.API_HOST

    def get_full_url(self):
        """Gets the full URL for API access."""
        return f"http://{self.get_host_address()}:{self.config.API_PORT}/chat"

    def copy_host_address(self):
        QApplication.clipboard().setText(self.get_host_address())
        self.show_status_message("Host address copied to clipboard!")

    def copy_full_url(self):
        QApplication.clipboard().setText(self.get_full_url())
        self.show_status_message("Full API URL copied to clipboard!")

    def show_status_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Info")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def update_port(self, new_port):
        self.config.API_PORT = new_port
        self.url_display.setText(self.get_full_url())
        self.show_status_message("Port updated. Restart the application for changes to take effect.")

    def toggle_google_search(self, state):
        is_enabled = state == Qt.CheckState.Checked.value
        self.config.ENABLE_GOOGLE_FALLBACK = is_enabled
        self.show_status_message(f"Google Search fallback has been {'enabled' if is_enabled else 'disabled'}.")

    def toggle_dark_mode(self, state):
        is_enabled = state == Qt.CheckState.Checked.value
        self.config.DARK_MODE = is_enabled
        if hasattr(self.app_instance, "gui") and self.app_instance.gui:
            self.app_instance.gui.apply_dark_mode(is_enabled)
        self.show_status_message(f"{'Dark' if is_enabled else 'Light'} mode is now active.")

    def update_confidence_threshold(self, value):
        self.config.CONFIDENCE_THRESHOLD = value
        self.show_status_message(f"Confidence threshold updated to {value:.2f}")
