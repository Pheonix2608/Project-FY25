import json
import sqlite3
import os
from datetime import datetime
from passlib.context import CryptContext
from utils.database import get_db_connection, initialize_database

def migrate_api_keys(pwd_context):
    api_keys_file = 'utils/api_keys.json'
    if not os.path.exists(api_keys_file):
        print("api_keys.json not found, skipping migration.")
        return

    with open(api_keys_file, 'r') as f:
        api_keys_data = json.load(f)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        for user_id, data in api_keys_data.items():
            try:
                cursor.execute(
                    """
                    INSERT INTO api_keys (key_hash, user_id, created_at, expires_at, rate_limit_per_minute, rate_limit_per_day)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data['key_hash'],
                        user_id,
                        datetime.fromisoformat(data['created_at']),
                        datetime.fromisoformat(data['expires_at']),
                        data.get('rate_limit', {}).get('calls_per_minute', 60),
                        data.get('rate_limit', {}).get('calls_per_day', 1000)
                    )
                )
            except sqlite3.IntegrityError:
                print(f"User ID {user_id} already exists in the database. Skipping.")
        conn.commit()
    print("API keys migrated successfully.")

def migrate_api_sessions():
    api_sessions_file = 'data/api_sessions.json'
    if not os.path.exists(api_sessions_file):
        print("api_sessions.json not found, skipping migration.")
        return

    with open(api_sessions_file, 'r') as f:
        api_sessions_data = json.load(f)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        for session in api_sessions_data:
            try:
                cursor.execute(
                    """
                    INSERT INTO api_sessions (api_key, user_id, timestamp, request_data, response_data)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "migrated_key",  # API key is not stored in the old format
                        session['user_id'],
                        datetime.fromisoformat(session['timestamp']),
                        json.dumps({"message": session.get("message")}),
                        json.dumps({
                            "response": session.get("response"),
                            "intent": session.get("intent"),
                            "confidence": session.get("confidence")
                        })
                    )
                )
            except Exception as e:
                print(f"Error migrating session for user {session.get('user_id')}: {e}")
        conn.commit()
    print("API sessions migrated successfully.")

if __name__ == '__main__':
    initialize_database()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    print("Starting data migration...")
    migrate_api_keys(pwd_context)
    migrate_api_sessions()
    print("Data migration complete.")