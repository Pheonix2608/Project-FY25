import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join('data', 'chatbot.db')
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def get_db_connection():
    """Establishes a connection to the SQLite database.

    This function connects to the database specified by `DB_FILE` and
    configures the connection to return rows as dictionary-like objects.

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database and creates tables if they don't exist.

    This function sets up the necessary tables (`api_keys`, `api_sessions`)
    for the application to function correctly. It is called automatically
    when this module is imported.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create api_keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT NOT NULL,
                user_id TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                rate_limit_per_minute INTEGER DEFAULT 60,
                rate_limit_per_day INTEGER DEFAULT 1000
            )
        """)

        # Create api_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_data TEXT,
                response_data TEXT
            )
        """)

        conn.commit()

# Initialize the database when this module is imported
initialize_database()