"""
Database migration utilities for handling database schema updates.
"""
import sqlite3
import os
from utils.logger import get_logger
from utils.database import get_db_connection, DB_FILE

logger = get_logger(__name__)

def get_db_version():
    """Gets the current database version."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS db_version (
                    version INTEGER PRIMARY KEY
                )
            """)
            cursor.execute("SELECT version FROM db_version")
            result = cursor.fetchone()
            return result['version'] if result else 0
    except Exception as e:
        logger.error(f"Failed to get database version: {e}")
        return 0

def set_db_version(version):
    """Sets the database version."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM db_version")
            cursor.execute("INSERT INTO db_version (version) VALUES (?)", (version,))
            conn.commit()
            logger.info(f"Database version set to {version}")
    except Exception as e:
        logger.error(f"Failed to set database version: {e}")
        raise

def migrate_to_v1():
    """
    Migration to version 1:
    - Add api_key column to api_keys table
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if api_key column exists
            cursor.execute("PRAGMA table_info(api_keys)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            if 'api_key' not in columns:
                logger.info("Adding api_key column to api_keys table...")
                # Create temporary table with new schema
                cursor.execute("""
                    CREATE TABLE api_keys_new (
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
                
                # Copy data from old table to new table
                cursor.execute("""
                    INSERT INTO api_keys_new (id, key_hash, user_id, created_at, expires_at, 
                                            rate_limit_per_minute, rate_limit_per_day)
                    SELECT id, key_hash, user_id, created_at, expires_at, 
                           rate_limit_per_minute, rate_limit_per_day
                    FROM api_keys
                """)
                
                # Drop old table and rename new table
                cursor.execute("DROP TABLE api_keys")
                cursor.execute("ALTER TABLE api_keys_new RENAME TO api_keys")
                
                logger.info("Successfully added api_key column")
            else:
                logger.info("api_key column already exists")
            
            conn.commit()
            set_db_version(1)
            return True
            
    except Exception as e:
        logger.error(f"Migration to version 1 failed: {e}")
        return False

def run_migrations():
    """Runs all pending database migrations."""
    try:
        current_version = get_db_version()
        logger.info(f"Current database version: {current_version}")
        
        if current_version < 1:
            logger.info("Running migration to version 1...")
            if migrate_to_v1():
                logger.info("Migration to version 1 completed successfully")
            else:
                logger.error("Migration to version 1 failed")
                return False
        
        logger.info("All migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return False

if __name__ == "__main__":
    run_migrations()