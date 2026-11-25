"""Logging configuration for the application."""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure application logging."""
    logger = logging.getLogger("prospect_discovery")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logging()


def log_request(query: str, client_ip: str, success: bool, prospect_count: int, duration_ms: float):
    """Log API request for monitoring."""
    logger.info(
        f"Request: query='{query[:50]}...' ip={client_ip} "
        f"success={success} prospects={prospect_count} duration={duration_ms:.0f}ms"
    )


def log_error(operation: str, error: Exception, context: Optional[dict] = None):
    """Log errors with context."""
    logger.error(
        f"Error in {operation}: {type(error).__name__}: {error}",
        extra={"context": context or {}}
    )