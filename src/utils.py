"""Utility functions for logging and hashing."""

import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "lead_scraper") -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # File handler - daily log file
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def generate_lead_hash(username: str, platform: str, text: str) -> str:
    """
    Generate a unique hash for a lead to detect duplicates.

    Args:
        username: Author username
        platform: Platform name (e.g., 'youtube')
        text: Comment text

    Returns:
        SHA-256 hash string
    """
    unique_string = f"{username}|{platform}|{text}"
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()


def detect_language(text: str) -> Optional[str]:
    """
    Detect comment language using langdetect library.

    Args:
        text: Comment text to analyze

    Returns:
        Language code ('en', 'hi', 'mr') if supported, None otherwise
    """
    try:
        from langdetect import detect, LangDetectException

        if not text or not text.strip():
            return None

        lang = detect(text)

        # Only process English, Hindi, and Marathi
        if lang in ['en', 'hi', 'mr']:
            return lang

        return None

    except LangDetectException:
        # Language detection failed (text too short, ambiguous, etc.)
        return None
    except ImportError:
        # langdetect not installed - log warning and continue
        logger = logging.getLogger(__name__)
        logger.warning("langdetect library not installed. Skipping language detection.")
        return 'en'  # Default to English if library not available
