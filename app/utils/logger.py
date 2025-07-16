import logging
import os
from datetime import datetime
from pathlib import Path
from app.config.settings import LOGS_DIR


def setup_logger():
    """Setup and configure logger with info and error handlers"""

    # Create today's log directory
    today_str = datetime.now().strftime("%Y_%m_%d_logs")
    today_dir = Path(LOGS_DIR) / today_str
    today_dir.mkdir(parents=True, exist_ok=True)

    # Define log file paths
    info_log_file = today_dir / "info.log"
    error_log_file = today_dir / "error.log"

    # Create logger
    logger = logging.getLogger("interview_system")
    logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Info handler (INFO and above)
    info_handler = logging.FileHandler(info_log_file)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Error handler (ERROR and above only)
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger


# Initialize logger instance
logger = setup_logger()


def log_info(message: str):
    """Log info message"""
    logger.info(message)


def log_error(message: str, exc_info=True):
    """Log error message"""
    logger.error(message, exc_info=exc_info)