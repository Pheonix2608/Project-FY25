# admin/tabs/api_key_management_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QInputDialog
)

class ApiKeyManagementTab(QWidget):
    """A widget for managing API keys in the admin panel.

    This tab provides a user interface for viewing, generating, modifying,
    and deleting API keys.
    """
    def __init__(self, app_instance):
        """Initializes the API Key Management tab.

        Args:
            app_instance (ChatbotApp): The main application instance.
        """
        super().__init__()
        self.app_instance = app_instance
        self.init_ui()
        self.refresh_api_keys_tab()

    def init_ui(self):
        """Initializes the UI components of the tab."""
        layout = QVBoxLayout(self)

        self.api_keys_table = QTableWidget()
        self.api_keys_table.setColumnCount(4)
        self.api_keys_table.setHorizontalHeaderLabels(["User ID", "Created At", "Expires At", "Rate Limits"])
        self.api_keys_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.api_keys_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.api_keys_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        btn_layout = QHBoxLayout()
        self.generate_key_button = QPushButton("Generate Key")
        self.modify_key_button = QPushButton("Modify User ID")
        self.delete_key_button = QPushButton("Delete Key")
        self.refresh_keys_button = QPushButton("Refresh")

        btn_layout.addWidget(self.generate_key_button)
        btn_layout.addWidget(self.modify_key_button)
        btn_layout.addWidget(self.delete_key_button)
        btn_layout.addWidget(self.refresh_keys_button)

        layout.addWidget(self.api_keys_table)
        layout.addLayout(btn_layout)

        self.generate_key_button.clicked.connect(self.generate_api_key)
        self.modify_key_button.clicked.connect(self.modify_api_key)
        self.delete_key_button.clicked.connect(self.delete_api_key)
        self.refresh_keys_button.clicked.connect(self.refresh_api_keys_tab)

        self.setLayout(layout)

    def refresh_api_keys_tab(self):
        """Refreshes the table with the latest list of API keys."""
        try:
            keys = self.app_instance.api_key_manager.list_all_api_keys()
            self.api_keys_table.setRowCount(0)
            for user_id, data in keys.items():
                row_position = self.api_keys_table.rowCount()
                self.api_keys_table.insertRow(row_position)
                self.api_keys_table.setItem(row_position, 0, QTableWidgetItem(user_id))
                self.api_keys_table.setItem(row_position, 1, QTableWidgetItem(data.get("created_at")))
                self.api_keys_table.setItem(row_position, 2, QTableWidgetItem(data.get("expires_at")))
                self.api_keys_table.setItem(row_position, 3, QTableWidgetItem(str(data.get("rate_limit"))))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load API keys: {e}")

    def generate_api_key(self):
        """Handles the 'Generate Key' button click event.

        Opens a dialog to get a user ID, then calls the API key manager
        to create a new key and displays it to the user.
        """
        user_id, ok = QInputDialog.getText(self, "Generate API Key", "Enter User ID:")
        if ok and user_id:
            try:
                new_key = self.app_instance.api_key_manager.generate_api_key(user_id)
                QMessageBox.information(self, "API Key Generated", f"New API Key for {user_id}:\n\n{new_key}\n\nPlease save this key, it will not be shown again.")
                self.refresh_api_keys_tab()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate API key: {e}")

    def modify_api_key(self):
        """Handles the 'Modify User ID' button click event.

        Allows changing the user ID associated with a selected API key.
        """
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an API key to modify.")
            return

        selected_row = selected_rows[0].row()
        old_user_id = self.api_keys_table.item(selected_row, 0).text()

        new_user_id, ok = QInputDialog.getText(self, "Modify User ID", f"Enter new User ID for '{old_user_id}':")
        if ok and new_user_id:
            try:
                success = self.app_instance.api_key_manager.modify_api_key_user(old_user_id, new_user_id)
                if success:
                    QMessageBox.information(self, "Success", f"User ID for key has been changed to {new_user_id}.")
                    self.refresh_api_keys_tab()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to modify User ID. The new User ID might already exist.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to modify API key: {e}")

    def delete_api_key(self):
        """Handles the 'Delete Key' button click event.

        Deletes the selected API key after a confirmation dialog.
        """
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an API key to delete.")
            return

        selected_row = selected_rows[0].row()
        user_id = self.api_keys_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "Delete API Key", f"Are you sure you want to delete the API key for '{user_id}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.app_instance.api_key_manager.delete_api_key(user_id)
                if success:
                    QMessageBox.information(self, "Success", f"API key for {user_id} has been deleted.")
                    self.refresh_api_keys_tab()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to delete API key.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete API key: {e}")
