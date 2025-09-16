# admin/tabs/chat_tester_tab.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from datetime import datetime

class ChatTesterTab(QWidget):
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.conversation_log = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.setLayout(layout)

    def send_message(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.display_message("User", user_input)
        self.input_field.clear()

        response_data = self.app_instance.process_input(user_input)
        response = response_data.get("response", "Sorry, something went wrong.")
        confidence = response_data.get("confidence", 0.0)
        intent = response_data.get("intent", "unknown")

        response_with_confidence = f"{response} (Intent: {intent}, Confidence: {confidence:.2%})"
        self.display_message("Bot", response_with_confidence)

    def display_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
        self.conversation_log.append({"time": timestamp, "sender": sender, "text": message})
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
