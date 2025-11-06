import secrets
import sqlite3
from datetime import datetime, timedelta
import hashlib
from .database import get_db_connection

class APIKeyManager:
    def __init__(self):
        pass  # No initialization needed for hashlib

    def generate_api_key(self, user_id: str, expiration_days: int = 30) -> str:
        try:
            if not user_id or not isinstance(user_id, str):
                raise ValueError("User ID must be a non-empty string")
                
            # Generate a random API key
            api_key = secrets.token_urlsafe(32)
            # Hash the API key using SHA256
            hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
            expires_at = datetime.now() + timedelta(days=expiration_days)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """INSERT INTO api_keys 
                           (key_hash, api_key, user_id, expires_at) 
                           VALUES (?, ?, ?, ?)""",
                        (hashed_key, api_key, user_id, expires_at)
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    raise ValueError(f"User ID '{user_id}' already exists.")
                except sqlite3.OperationalError as db_error:
                    raise RuntimeError(f"Database error: {str(db_error)}")
                except Exception as e:
                    raise RuntimeError(f"Unexpected database error: {str(e)}")
            
            return api_key
        except Exception as e:
            # Log the full error with stack trace
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception("Failed to generate API key")
            raise

    def verify_api_key(self, api_key: str) -> str | None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key_hash, user_id, expires_at FROM api_keys")
            rows = cursor.fetchall()

            # Hash the provided API key
            hashed_input = hashlib.sha256(api_key.encode()).hexdigest()

            for row in rows:
                # Convert sqlite3.Row to dict for safer access
                row_dict = dict(row)
                if hashed_input == row_dict['key_hash']:
                    expires_at = datetime.fromisoformat(row_dict['expires_at'])
                    if expires_at > datetime.now():
                        return row_dict['user_id']
        return None

    def get_rate_limits(self, user_id: str) -> dict | None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rate_limit_per_minute, rate_limit_per_day FROM api_keys WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                # Convert sqlite3.Row to dict for safer access
                row_dict = dict(row)
                return {"calls_per_minute": row_dict['rate_limit_per_minute'], "calls_per_day": row_dict['rate_limit_per_day']}
        return None

    def update_rate_limits(self, user_id: str, calls_per_minute: int, calls_per_day: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE api_keys SET rate_limit_per_minute = ?, rate_limit_per_day = ? WHERE user_id = ?",
                (calls_per_minute, calls_per_day, user_id)
            )
            conn.commit()

    def list_all_api_keys(self) -> dict:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, api_key, key_hash, created_at, expires_at, 
                       rate_limit_per_minute, rate_limit_per_day 
                FROM api_keys
            """)
            rows = cursor.fetchall()

            keys_to_return = {}
            for row in rows:
                # Convert sqlite3.Row to dict for safer access
                row_dict = dict(row)
                keys_to_return[row_dict['user_id']] = {
                    "api_key": row_dict.get('api_key', 'Not Available'),
                    "key_hash": row_dict['key_hash'],
                    "created_at": row_dict['created_at'],
                    "expires_at": row_dict['expires_at'],
                    "rate_limit": {
                        "calls_per_minute": row_dict['rate_limit_per_minute'],
                        "calls_per_day": row_dict['rate_limit_per_day']
                    }
                }
            return keys_to_return

    def delete_api_key(self, user_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_keys WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def modify_api_key_user(self, old_user_id: str, new_user_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE api_keys SET user_id = ? WHERE user_id = ?", (new_user_id, old_user_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.IntegrityError:
                # New user_id is not unique
                return False