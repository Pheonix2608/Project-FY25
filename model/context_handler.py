
# ==============================================================================
# model/context_handler.py
# A simple class to store and retrieve conversation context.
# ==============================================================================
from collections import deque

class ContextHandler:
    """Manages the conversation context for multi-turn dialogue.

    This class uses a deque to maintain a sliding window of the most
    recent turns in a conversation.
    """
    def __init__(self, window_size=3):
        """Initializes the ContextHandler.

        Args:
            window_size (int): The number of recent conversation turns to
                store in the context.
        """
        self.window_size = window_size
        self.context = deque(maxlen=window_size)

    def add_user_query(self, query):
        """Adds a user's query to the conversation context.

        Args:
            query (str): The text of the user's message.
        """
        self.context.append({"role": "user", "text": query})

    def add_bot_response(self, response):
        """Adds the bot's response to the conversation context.

        Args:
            response (str): The text of the bot's reply.
        """
        self.context.append({"role": "bot", "text": response})

    def get_context(self):
        """Retrieves the current conversation context.

        Returns:
            list: A list of dictionaries, where each dictionary represents
                a turn in the conversation.
        """
        return list(self.context)

    def clear_context(self):
        """Clears all entries from the conversation context."""
        self.context.clear()

