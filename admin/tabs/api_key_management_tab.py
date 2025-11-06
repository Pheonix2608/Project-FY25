# admin/tabs/api_key_management_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QInputDialog, QDialog, QLabel,
    QLineEdit, QTextEdit, QApplication, QMenu
)
from PyQt6.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)

class ApiKeyManagementTab(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.init_ui()
        self.refresh_api_keys_tab()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.api_keys_table = QTableWidget()
        self.api_keys_table.setColumnCount(5)
        self.api_keys_table.setHorizontalHeaderLabels(["User ID", "API Key", "Created At", "Expires At", "Rate Limits"])
        self.api_keys_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.api_keys_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.api_keys_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        # Enable sorting
        self.api_keys_table.setSortingEnabled(True)

        btn_layout = QHBoxLayout()
        self.generate_key_button = QPushButton("Generate Key")
        self.modify_key_button = QPushButton("Modify User ID")
        self.delete_key_button = QPushButton("Delete Selected")
        self.group_keys_button = QPushButton("Group Selected")
        self.refresh_keys_button = QPushButton("Refresh")

        btn_layout.addWidget(self.generate_key_button)
        btn_layout.addWidget(self.modify_key_button)
        btn_layout.addWidget(self.delete_key_button)
        btn_layout.addWidget(self.group_keys_button)
        btn_layout.addWidget(self.refresh_keys_button)

        layout.addWidget(self.api_keys_table)
        layout.addLayout(btn_layout)

        # Apply adaptive styling based on theme
        self.update_table_style()
        
        # Set up context menu
        self.api_keys_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.api_keys_table.customContextMenuRequested.connect(self.show_context_menu)
        
    def update_table_style(self):
        """Updates table styling based on current theme."""
        is_dark = hasattr(self.app_instance.config, 'DARK_MODE') and self.app_instance.config.DARK_MODE
        
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
        
        self.api_keys_table.horizontalHeader().setStyleSheet(header_style)
        self.api_keys_table.verticalHeader().setStyleSheet(header_style)
        
    def show_context_menu(self, pos):
        """Shows context menu for API key operations."""
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        menu = QMenu(self)
        
        # Add menu items
        copy_user_id = menu.addAction("Copy User ID")
        copy_api_key = menu.addAction("Copy API Key")
        menu.addSeparator()
        show_details = menu.addAction("Show Details")
        menu.addSeparator()
        modify_action = menu.addAction("Modify User ID")
        delete_action = menu.addAction("Delete")
        
        # Get the global position
        global_pos = self.api_keys_table.mapToGlobal(pos)
        
        # Show menu and get selected action
        action = menu.exec(global_pos)
        
        if not action:
            return
            
        # Handle the selected action
        row = selected_rows[0].row()
        user_id = self.api_keys_table.item(row, 0).text()
        
        if action == copy_user_id:
            self.copy_to_clipboard(user_id)
        elif action == copy_api_key:
            # Get the full API key from the item's data
            api_key = self.api_keys_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            if api_key:
                self.copy_to_clipboard(api_key)
                QMessageBox.information(self, "Copied", "API Key has been copied to clipboard.")
        elif action == show_details:
            self.show_api_key_details(user_id)
        elif action == modify_action:
            self.modify_api_key()
        elif action == delete_action:
            self.delete_api_key()
            
    def show_api_key_details(self, user_id):
        """Shows detailed information about the selected API key."""
        keys = self.app_instance.api_key_manager.list_all_api_keys()
        if user_id not in keys:
            return
            
        key_data = keys[user_id]
        api_key = key_data.get("api_key", "N/A")
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"API Key Details - {user_id}")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Create details layout
        details = [
            ("User ID:", user_id),
            ("API Key:", api_key),
            ("Key Hash:", key_data.get("key_hash", "N/A")),
            ("Created:", key_data.get("created_at", "N/A")),
            ("Expires:", key_data.get("expires_at", "N/A")),
            ("Rate Limit (per minute):", str(key_data.get("rate_limit", {}).get("calls_per_minute", "N/A"))),
            ("Rate Limit (per day):", str(key_data.get("rate_limit", {}).get("calls_per_day", "N/A")))
        ]
        
        for label, value in details:
            row_layout = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold;")
            value_widget = QLineEdit(value)
            value_widget.setReadOnly(True)
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            layout.addLayout(row_layout)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()

        # Connect button signals
        self.generate_key_button.clicked.connect(self.generate_api_key)
        self.modify_key_button.clicked.connect(self.modify_api_key)
        self.delete_key_button.clicked.connect(self.delete_api_key)
        self.group_keys_button.clicked.connect(self.group_selected_keys)
        self.refresh_keys_button.clicked.connect(self.refresh_api_keys_tab)

    def refresh_api_keys_tab(self):
        try:
            logger.info("Refreshing API keys table...")
            if not self.app_instance:
                raise RuntimeError("app_instance is None - AdminPanel not properly initialized")
            if not self.app_instance.api_key_manager:
                raise RuntimeError("api_key_manager is None - ChatbotApp not properly initialized")
            
            keys = self.app_instance.api_key_manager.list_all_api_keys()
            logger.debug(f"Retrieved {len(keys)} API keys")
            
            self.api_keys_table.setRowCount(0)
            if not keys:
                # Add placeholder row when no keys exist
                self.api_keys_table.insertRow(0)
                placeholder = QTableWidgetItem("No API keys found - Use 'Generate Key' to create one")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.api_keys_table.setItem(0, 0, placeholder)
                self.api_keys_table.setSpan(0, 0, 1, 5)  # Span all columns
                logger.info("No API keys found in database")
                return
                
            for user_id, data in keys.items():
                row_position = self.api_keys_table.rowCount()
                self.api_keys_table.insertRow(row_position)
                
                # Create table items
                user_id_item = QTableWidgetItem(user_id)
                # Get API key and create a masked version for display
                api_key = data.get("api_key", "")
                masked_key = f"{api_key[:8]}..." if api_key else "Not Available"
                api_key_item = QTableWidgetItem(masked_key)
                api_key_item.setData(Qt.ItemDataRole.UserRole, api_key)  # Store full key
                
                created_item = QTableWidgetItem(data.get("created_at"))
                expires_item = QTableWidgetItem(data.get("expires_at"))
                rate_limit = data.get("rate_limit", {})
                rate_limit_text = f"Per min: {rate_limit.get('calls_per_minute', 'N/A')}, Per day: {rate_limit.get('calls_per_day', 'N/A')}"
                rate_limit_item = QTableWidgetItem(rate_limit_text)
                
                # Set items as non-editable
                for item in [user_id_item, api_key_item, created_item, expires_item, rate_limit_item]:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Add items to table
                self.api_keys_table.setItem(row_position, 0, user_id_item)
                self.api_keys_table.setItem(row_position, 1, api_key_item)
                self.api_keys_table.setItem(row_position, 2, created_item)
                self.api_keys_table.setItem(row_position, 3, expires_item)
                self.api_keys_table.setItem(row_position, 4, rate_limit_item)

                # Set tooltip for API key column
                api_key_item.setToolTip("Right-click for options to copy or view full key")
            logger.info(f"Successfully populated table with {len(keys)} API keys")
            
        except Exception as e:
            error_msg = f"Failed to load API keys: {str(e)}"
            logger.exception(error_msg)  # This logs the full stack trace
            QMessageBox.critical(self, "Error", error_msg)

    def copy_to_clipboard(self, text):
        """Helper method to copy text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
    def show_api_key_dialog(self, user_id, api_key):
        """Shows a custom dialog with the new API key and a copy button"""
        dialog = QDialog(self)
        dialog.setWindowTitle("API Key Generated")
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # Key info section
        key_info = QLabel(f"New API Key for {user_id}:")
        key_info.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(key_info)
        
        # API Key section with copy button
        key_layout = QHBoxLayout()
        key_text = QLineEdit(api_key)
        key_text.setReadOnly(True)
        key_text.setMinimumWidth(400)
        copy_key_btn = QPushButton("Copy Key")
        copy_key_btn.clicked.connect(lambda: self.copy_to_clipboard(api_key))
        key_layout.addWidget(key_text)
        key_layout.addWidget(copy_key_btn)
        layout.addLayout(key_layout)
        
        # Warning message
        warning = QLabel("Please save this key, it will not be shown again.")
        warning.setStyleSheet("color: red;")
        layout.addWidget(warning)
        
        # Curl example section
        curl_label = QLabel("Test with curl:")
        layout.addWidget(curl_label)
        
        curl_command = (f"curl -X POST http://localhost:8080/chat \\\n"
                       f"  -H \"X-API-Key: {api_key}\" \\\n"
                       f"  -H \"Content-Type: application/json\" \\\n"
                       f"  -d \"{{\\\"message\\\": \\\"Hello\\\"}}\"")
        
        curl_text = QTextEdit()
        curl_text.setPlainText(curl_command)
        curl_text.setReadOnly(True)
        curl_text.setMaximumHeight(100)
        layout.addWidget(curl_text)
        
        # Copy curl command button
        copy_curl_btn = QPushButton("Copy Curl Command")
        copy_curl_btn.clicked.connect(lambda: self.copy_to_clipboard(curl_command))
        layout.addWidget(copy_curl_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def generate_api_key(self):
        user_id, ok = QInputDialog.getText(self, "Generate API Key", "Enter User ID:")
        if ok and user_id:
            try:
                logger.info(f"Attempting to generate API key for user: {user_id}")
                if not self.app_instance:
                    raise RuntimeError("App instance is not initialized")
                if not self.app_instance.api_key_manager:
                    raise RuntimeError("API key manager is not initialized")
                
                new_key = self.app_instance.api_key_manager.generate_api_key(user_id)
                logger.info(f"Successfully generated API key for user: {user_id}")
                
                # Show custom dialog with copy button
                self.show_api_key_dialog(user_id, new_key)
                self.refresh_api_keys_tab()
                
            except Exception as e:
                error_msg = f"Failed to generate API key: {str(e)}"
                logger.exception(error_msg)
                QMessageBox.critical(self, "Error", error_msg)

    def modify_api_key(self):
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
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select at least one API key to delete.")
            return

        user_ids = [self.api_keys_table.item(row.row(), 0).text() for row in selected_rows]
        user_list = "\n".join(user_ids)

        reply = QMessageBox.question(self, "Delete API Keys", 
                                   f"Are you sure you want to delete the API keys for:\n{user_list}",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success_count = 0
                for user_id in user_ids:
                    if self.app_instance.api_key_manager.delete_api_key(user_id):
                        success_count += 1

                if success_count > 0:
                    QMessageBox.information(self, "Success", 
                                         f"Successfully deleted {success_count} API key(s).")
                    self.refresh_api_keys_tab()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to delete any API keys.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete API keys: {e}")

    def group_selected_keys(self):
        """Groups selected API keys together for batch operations."""
        selected_rows = self.api_keys_table.selectionModel().selectedRows()
        if len(selected_rows) < 2:
            QMessageBox.warning(self, "Warning", "Please select at least two API keys to group.")
            return

        user_ids = [self.api_keys_table.item(row.row(), 0).text() for row in selected_rows]
        
        # Create a text summary of selected keys
        summary = "\n".join([f"- {uid}" for uid in user_ids])
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Grouped API Keys")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"Selected {len(user_ids)} API keys:\n{summary}"))
        
        # Add buttons for batch operations
        batch_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete All")
        delete_btn.clicked.connect(lambda: self.batch_delete_keys(user_ids))
        
        modify_btn = QPushButton("Modify All")
        modify_btn.clicked.connect(lambda: self.batch_modify_keys(user_ids))
        
        batch_layout.addWidget(delete_btn)
        batch_layout.addWidget(modify_btn)
        layout.addLayout(batch_layout)
        
        dialog.setLayout(layout)
        dialog.exec()

    def batch_delete_keys(self, user_ids):
        """Deletes multiple API keys at once."""
        reply = QMessageBox.question(self, "Batch Delete",
                                   f"Delete {len(user_ids)} API keys?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            for user_id in user_ids:
                if self.app_instance.api_key_manager.delete_api_key(user_id):
                    success_count += 1
            
            QMessageBox.information(self, "Batch Delete Complete", 
                                  f"Successfully deleted {success_count} of {len(user_ids)} API keys.")
            self.refresh_api_keys_tab()

    def batch_modify_keys(self, user_ids):
        """Modifies multiple API keys at once."""
        new_prefix, ok = QInputDialog.getText(self, "Batch Modify",
                                            "Enter new user ID prefix for selected keys:")
        if ok and new_prefix:
            success_count = 0
            for i, old_id in enumerate(user_ids):
                new_id = f"{new_prefix}_{i+1}"
                if self.app_instance.api_key_manager.modify_api_key_user(old_id, new_id):
                    success_count += 1
            
            QMessageBox.information(self, "Batch Modify Complete",
                                  f"Successfully modified {success_count} of {len(user_ids)} API keys.")
            self.refresh_api_keys_tab()


