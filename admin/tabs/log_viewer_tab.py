# admin/tabs/log_viewer_tab.py

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtCore import QFileSystemWatcher, pyqtSignal, QObject

class LogSignalEmitter(QObject):
    """A simple QObject that emits a signal with log updates.

    This is used to safely update the GUI from the file watcher thread.
    """
    log_updated = pyqtSignal(str)

class LogViewerTab(QWidget):
    """A widget for viewing and monitoring log files in real-time.

    This tab allows users to select a log file from a directory, view its
    contents, and see new log entries as they are written to the file.
    """
    def __init__(self, log_dir):
        """Initializes the Log Viewer tab.

        Args:
            log_dir (str): The directory where log files are stored.
        """
        super().__init__()
        self.log_dir = log_dir
        self.log_files = self.get_log_files()
        self.current_log_file = None
        self.last_position = 0

        self.signal_emitter = LogSignalEmitter()
        self.signal_emitter.log_updated.connect(self.append_log_content)

        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.on_log_file_changed)

        self.init_ui()
        if self.log_files:
            self.load_log_file(self.log_files[0])

    def get_log_files(self):
        """Gets a list of .log files from the specified log directory.

        Returns:
            list: A sorted list of log file names.
        """
        if not os.path.exists(self.log_dir):
            return []
        return sorted([f for f in os.listdir(self.log_dir) if f.endswith('.log')])

    def init_ui(self):
        """Initializes the UI components of the tab."""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.log_file_dropdown = QComboBox()
        self.log_file_dropdown.addItems(self.log_files)
        self.log_file_dropdown.currentTextChanged.connect(self.on_log_file_selected)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_log_files)

        toolbar_layout.addWidget(self.log_file_dropdown)
        toolbar_layout.addWidget(refresh_button)
        layout.addLayout(toolbar_layout)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        self.setLayout(layout)

    def refresh_log_files(self):
        """Refreshes the list of available log files in the dropdown."""
        self.log_files = self.get_log_files()
        self.log_file_dropdown.clear()
        self.log_file_dropdown.addItems(self.log_files)

    def on_log_file_selected(self, filename):
        """Handles the selection of a new log file from the dropdown.

        Args:
            filename (str): The name of the selected log file.
        """
        if filename:
            self.load_log_file(filename)

    def load_log_file(self, filename):
        """Loads and displays the full content of a log file.

        Args:
            filename (str): The name of the log file to load.
        """
        if self.current_log_file:
            self.watcher.removePath(self.current_log_file)

        self.current_log_file = os.path.join(self.log_dir, filename)
        self.watcher.addPath(self.current_log_file)
        self.last_position = 0

        try:
            with open(self.current_log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.log_display.setPlainText(content)
                self.last_position = f.tell()
                self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())
        except Exception as e:
            self.log_display.setPlainText(f"Error loading log file: {e}")

    def on_log_file_changed(self, path):
        """A slot that handles the `fileChanged` signal from QFileSystemWatcher.

        This method reads only the new content added to the log file since
        the last read and emits a signal to update the GUI.

        Args:
            path (str): The path to the modified file.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                f.seek(self.last_position)
                new_content = f.read()
                if new_content:
                    self.last_position = f.tell()
                    self.signal_emitter.log_updated.emit(new_content)
        except Exception as e:
            print(f"Error reading log file: {e}")

    def append_log_content(self, new_content):
        """Appends new content to the log display text edit.

        Args:
            new_content (str): The new log text to append.
        """
        self.log_display.append(new_content)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())