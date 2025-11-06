# admin/tabs/api_session_viewer_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from utils.database import get_db_connection

class ApiSessionViewerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_api_sessions_tab()
        
    def update_table_style(self):
        """Updates table styling based on current theme."""
        # Get dark mode setting from parent widget's window
        window = self.window()
        is_dark = False
        if hasattr(window, 'app_instance') and hasattr(window.app_instance.config, 'DARK_MODE'):
            is_dark = window.app_instance.config.DARK_MODE
        
        if is_dark:
            header_style = """
                QHeaderView::section {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 5px;
                    border: 1px solid #3d3d3d;
                }
                QTableView {
                    gridline-color: #3d3d3d;
                    border: 1px solid #3d3d3d;
                }
            """
        else:
            header_style = """
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 5px;
                    border: 1px solid #ddd;
                }
                QTableView {
                    gridline-color: #ddd;
                    border: 1px solid #ddd;
                }
            """
        
        self.api_sessions_table.horizontalHeader().setStyleSheet(header_style)
        self.api_sessions_table.verticalHeader().setStyleSheet(header_style)

    def init_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by User ID:"))
        self.session_filter_input = QLineEdit()
        self.session_filter_input.textChanged.connect(self.refresh_api_sessions_tab)
        filter_layout.addWidget(self.session_filter_input)

        self.api_sessions_table = QTableWidget()
        self.api_sessions_table.setColumnCount(4)
        self.api_sessions_table.setHorizontalHeaderLabels(["Timestamp", "User ID", "Request", "Response"])
        self.api_sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Apply the initial styling
        self.update_table_style()

        self.refresh_sessions_button = QPushButton("Refresh")
        self.refresh_sessions_button.clicked.connect(self.refresh_api_sessions_tab)

        layout.addLayout(filter_layout)
        layout.addWidget(self.api_sessions_table)
        layout.addWidget(self.refresh_sessions_button)

        self.setLayout(layout)

    def fetch_sessions_from_db(self, filter_text=''):
        sessions = []
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT timestamp, user_id, api_key, request_data, response_data FROM api_sessions"
            params = []
            if filter_text:
                query += " WHERE user_id LIKE ?"
                params.append(f"%{filter_text}%")
            query += " ORDER BY timestamp DESC"

            cursor.execute(query, params)
            for row in cursor.fetchall():
                sessions.append(dict(row))
        return sessions

    def refresh_api_sessions_tab(self):
        try:
            filter_text = self.session_filter_input.text().strip()
            logs = self.fetch_sessions_from_db(filter_text)

            self.api_sessions_table.setRowCount(0)
            for log in logs:
                row_position = self.api_sessions_table.rowCount()
                self.api_sessions_table.insertRow(row_position)
                self.api_sessions_table.setItem(row_position, 0, QTableWidgetItem(log.get("timestamp")))
                self.api_sessions_table.setItem(row_position, 1, QTableWidgetItem(log.get("user_id")))
                self.api_sessions_table.setItem(row_position, 2, QTableWidgetItem(str(log.get("request_data"))))
                self.api_sessions_table.setItem(row_position, 3, QTableWidgetItem(str(log.get("response_data"))))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load API sessions: {e}")