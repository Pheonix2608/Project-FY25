import secrets
import sqlite3
from datetime import datetime, timedelta
from passlib.context import CryptContext
from .database import get_db_connection

class APIKeyManager:
    """Manages API keys, including creation, verification, and rate limiting.

    This class handles the lifecycle of API keys, storing them securely
    and providing methods to interact with them.
    """
    def __init__(self):
        """Initializes the APIKeyManager.

        Sets up the password hashing context for securing API keys.
        """
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def generate_api_key(self, user_id: str, expiration_days: int = 30) -> str:
        """Generates a new API key for a user.

        Args:
            user_id (str): The unique identifier for the user.
            expiration_days (int): The number of days until the key expires.

        Returns:
            str: The generated API key.

        Raises:
            ValueError: If the user_id already exists.
        """
        api_key = secrets.token_urlsafe(32)
        hashed_key = self.pwd_context.hash(api_key)

        expires_at = datetime.now() + timedelta(days=expiration_days)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO api_keys (key_hash, user_id, expires_at) VALUES (?, ?, ?)",
                    (hashed_key, user_id, expires_at)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # This will be raised if the user_id is not unique
                raise ValueError(f"User ID '{user_id}' already exists.")

        return api_key

    def verify_api_key(self, api_key: str) -> str | None:
        """Verifies an API key.

        Args:
            api_key (str): The API key to verify.

        Returns:
            str | None: The user_id associated with the key if valid and not
                expired, otherwise None.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key_hash, user_id, expires_at FROM api_keys")
            rows = cursor.fetchall()

            for row in rows:
                if self.pwd_context.verify(api_key, row['key_hash']):
                    expires_at = datetime.fromisoformat(row['expires_at'])
                    if expires_at > datetime.now():
                        return row['user_id']
        return None

    def get_rate_limits(self, user_id: str) -> dict | None:
        """Retrieves the rate limits for a given user.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            dict | None: A dictionary with rate limit information or None if
                the user is not found.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rate_limit_per_minute, rate_limit_per_day FROM api_keys WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {"calls_per_minute": row['rate_limit_per_minute'], "calls_per_day": row['rate_limit_per_day']}
        return None

    def update_rate_limits(self, user_id: str, calls_per_minute: int, calls_per_day: int):
        """Updates the rate limits for a user.

        Args:
            user_id (str): The user's unique identifier.
            calls_per_minute (int): The new rate limit for calls per minute.
            calls_per_day (int): The new rate limit for calls per day.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE api_keys SET rate_limit_per_minute = ?, rate_limit_per_day = ? WHERE user_id = ?",
                (calls_per_minute, calls_per_day, user_id)
            )
            conn.commit()

    def list_all_api_keys(self) -> dict:
        """Lists all API keys and their details.

        Returns:
            dict: A dictionary where keys are user_ids and values are
                details about the API key.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, created_at, expires_at, rate_limit_per_minute, rate_limit_per_day FROM api_keys")
            rows = cursor.fetchall()

            keys_to_return = {}
            for row in rows:
                keys_to_return[row['user_id']] = {
                    "created_at": row['created_at'],
                    "expires_at": row['expires_at'],
                    "rate_limit": {
                        "calls_per_minute": row['rate_limit_per_minute'],
                        "calls_per_day": row['rate_limit_per_day']
                    }
                }
            return keys_to_return

    def delete_api_key(self, user_id: str) -> bool:
        """Deletes an API key for a specific user.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            bool: True if a key was deleted, False otherwise.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_keys WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def modify_api_key_user(self, old_user_id: str, new_user_id: str) -> bool:
        """Changes the user_id associated with an API key.

        Args:
            old_user_id (str): The current user_id.
            new_user_id (str): The new user_id to associate with the key.

        Returns:
            bool: True if the update was successful, False otherwise (e.g.,
                if the new_user_id already exists).
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE api_keys SET user_id = ? WHERE user_id = ?", (new_user_id, old_user_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.IntegrityError:
                # New user_id is not unique
                return False