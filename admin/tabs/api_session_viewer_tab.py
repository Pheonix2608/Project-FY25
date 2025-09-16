# admin/tabs/api_session_viewer_tab.py

import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QMessageBox
)

class ApiSessionViewerTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()
        self.refresh_api_sessions_tab()

    def init_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by User ID:"))
        self.session_filter_input = QLineEdit()
        self.session_filter_input.textChanged.connect(self.refresh_api_sessions_tab)
        filter_layout.addWidget(self.session_filter_input)

        self.api_sessions_table = QTableWidget()
        self.api_sessions_table.setColumnCount(5)
        self.api_sessions_table.setHorizontalHeaderLabels(["Timestamp", "User ID", "Message", "Response", "Intent"])
        self.api_sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.refresh_sessions_button = QPushButton("Refresh")
        self.refresh_sessions_button.clicked.connect(self.refresh_api_sessions_tab)

        layout.addLayout(filter_layout)
        layout.addWidget(self.api_sessions_table)
        layout.addWidget(self.refresh_sessions_button)

        self.setLayout(layout)

    def refresh_api_sessions_tab(self):
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
