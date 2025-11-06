"""
migrate.py - Database Migration Script
Run this script to perform all database migrations in sequence.
"""

import sqlite3
import os
from datetime import datetime
from utils.logger import get_logger
import sys

logger = get_logger(__name__)

# Database configuration
DB_FILE = os.path.join('data', 'chatbot.db')

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Creates the initial database structure."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create version tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        
        # Create initial tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT NOT NULL,
                api_key TEXT,
                user_id TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                rate_limit_per_minute INTEGER DEFAULT 60,
                rate_limit_per_day INTEGER DEFAULT 1000
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_data TEXT,
                response_data TEXT,
                client_ip TEXT,
                endpoint TEXT
            )
        """)
        
        conn.commit()
        logger.info("Database initialized with base tables")

def get_current_version():
    """Gets the current database version."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(version) as version FROM db_version")
            result = cursor.fetchone()
            return result['version'] if result and result['version'] is not None else 0
    except Exception as e:
        logger.error(f"Failed to get database version: {e}")
        return 0

def record_migration(version, description):
    """Records a successful migration."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO db_version (version, description) VALUES (?, ?)",
                (version, description)
            )
            conn.commit()
            logger.info(f"Recorded migration version {version}: {description}")
    except Exception as e:
        logger.error(f"Failed to record migration: {e}")
        raise

def migration_001_add_api_key_column():
    """
    Migration 001: Add api_key column to api_keys table
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if api_key column exists
            cursor.execute("PRAGMA table_info(api_keys)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            if 'api_key' not in columns:
                logger.info("Adding api_key column to api_keys table...")
                cursor.execute("ALTER TABLE api_keys ADD COLUMN api_key TEXT")
                conn.commit()
                return True
            else:
                logger.info("api_key column already exists")
                return True
                
    except Exception as e:
        logger.error(f"Migration 001 failed: {e}")
        return False

def migration_002_add_session_tracking():
    """
    Migration 002: Add client_ip and endpoint columns to api_sessions
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check for existing columns
            cursor.execute("PRAGMA table_info(api_sessions)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            if 'client_ip' not in columns:
                cursor.execute("ALTER TABLE api_sessions ADD COLUMN client_ip TEXT")
                
            if 'endpoint' not in columns:
                cursor.execute("ALTER TABLE api_sessions ADD COLUMN endpoint TEXT")
                
            conn.commit()
            return True
                
    except Exception as e:
        logger.error(f"Migration 002 failed: {e}")
        return False

# List of all migrations
MIGRATIONS = [
    (1, "Add api_key column", migration_001_add_api_key_column),
    (2, "Add session tracking columns", migration_002_add_session_tracking),
]

def run_migrations(target_version=None):
    """
    Runs all pending migrations up to target_version.
    If target_version is None, runs all available migrations.
    """
    try:
        initialize_database()
        current_version = get_current_version()
        logger.info(f"Current database version: {current_version}")
        
        if target_version is None:
            target_version = max(m[0] for m in MIGRATIONS)
        
        if current_version >= target_version:
            logger.info("Database is up to date")
            return True
            
        success = True
        for version, description, migration_func in sorted(MIGRATIONS):
            if current_version < version <= target_version:
                logger.info(f"Running migration {version}: {description}")
                try:
                    if migration_func():
                        record_migration(version, description)
                        logger.info(f"Migration {version} completed successfully")
                    else:
                        success = False
                        logger.error(f"Migration {version} failed")
                        break
                except Exception as e:
                    success = False
                    logger.error(f"Error in migration {version}: {e}")
                    break
        
        final_version = get_current_version()
        logger.info(f"Final database version: {final_version}")
        return success
        
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Database Migration Tool")
    parser.add_argument(
        "--target",
        type=int,
        help="Target migration version. If not specified, runs all available migrations.",
        default=None
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show current database version and available migrations"
    )
    
    args = parser.parse_args()
    
    if args.info:
        current = get_current_version()
        latest = max(m[0] for m in MIGRATIONS)
        print(f"Current database version: {current}")
        print(f"Latest available version: {latest}")
        print("\nAvailable migrations:")
        for version, description, _ in sorted(MIGRATIONS):
            status = "Applied" if version <= current else "Pending"
            print(f"  [{status}] {version}: {description}")
    else:
        success = run_migrations(args.target)
        sys.exit(0 if success else 1)