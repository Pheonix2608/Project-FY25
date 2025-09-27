# ==============================================================================
# utils/logger.py
# Utility module for standardized logging with daily rotation.
# ==============================================================================
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import datetime

from config import Config

def get_logger(name):
    """Creates and configures a logger instance.

    This function sets up a logger with both console and file handlers.
    The file handler rotates daily, keeping a history of logs.

    Args:
        name (str): The name for the logger, typically the module's `__name__`.

    Returns:
        logging.Logger: A configured logger instance.
    """
    config = Config()

    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)

    if not logger.handlers:
        os.makedirs(config.LOG_DIR, exist_ok=True)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = TimedRotatingFileHandler(
            os.path.join(config.LOG_DIR, f'{config.LOG_FILE_PREFIX}.log'),
            when='midnight',
            interval=1,
            backupCount=7,
            delay=True  # Delay file creation until first write
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

