"""
Database connection management module.
"""
import sqlite3
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)
DB_FILE = os.path.join('data', 'chatbot.db')
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure database exists
if not os.path.exists(DB_FILE):
    logger.info("Database file not found. Please run migrate.py to initialize the database.")
    with get_db_connection() as conn:
        pass  # Just create the empty database file