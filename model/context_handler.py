
# ==============================================================================
# model/context_handler.py
# A simple class to store and retrieve conversation context.
# ==============================================================================
from collections import deque

class ContextHandler:
    """
    Manages the conversation context for multi-turn dialogue.
    """
    def __init__(self, window_size=3):
        """
        Initializes the context queue.
        
        Args:
            window_size (int): The number of recent turns to remember.
        """
        self.window_size = window_size
        self.context = deque(maxlen=window_size)

    def add_user_query(self, query):
        """
        Adds a user query to the context.
        """
        self.context.append({"role": "user", "text": query})

    def add_bot_response(self, response):
        """
        Adds a bot response to the context.
        """
        self.context.append({"role": "bot", "text": response})

    def get_context(self):
        """
        Returns the current conversation context.
        """
        return list(self.context)

    def clear_context(self):
        """
        Clears the conversation context.
        """
        self.context.clear()

