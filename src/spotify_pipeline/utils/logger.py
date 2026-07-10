# src/spotify_pipeline/utils/logger.py
import logging
import json
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Get structured JSON logger for pipeline.

    Usage:
        from spotify_pipeline.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Fetching artists")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Create handler — prints to terminal
    handler = logging.StreamHandler()

    # JSON formatter — structured output for CloudWatch/Datadog
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", '
        '"level": "%(levelname)s", '
        '"module": "%(name)s", '
        '"message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger