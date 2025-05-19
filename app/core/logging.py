"""
Logging utilities for the MindMeld application.

This module configures structured logging using loguru, provides request ID context,
and exposes helper functions for consistent, contextual logging throughout the app.
"""

import sys
import uuid
from contextvars import ContextVar

from app.core.config import settings
from loguru import logger

# Context variable to store request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Default to INFO if LOG_LEVEL isn't set
log_level: str = getattr(settings, "LOG_LEVEL", "INFO")

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[request_id]} | {message}",
    level=log_level,
    serialize=True,  # Enable JSON logs for production
    backtrace=True,
    diagnose=True,
)


def get_request_id() -> str:
    """
    Retrieve the current request ID from context.

    Returns:
        str: The current request ID, or an empty string if not set.
    """
    return request_id_var.get()


def set_request_id(request_id: str | None = None) -> str:
    """
    Set a request ID in the context for the current request.

    Args:
        request_id (str | None): The request ID to set. If None, a new UUID is generated.

    Returns:
        str: The request ID that was set.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def get_logger() -> logger.__class__:
    """
    Get a logger instance bound with the current request ID for contextual logging.

    Returns:
        loguru.Logger: Logger instance with request_id context.
    """
    return logger.bind(request_id=get_request_id())
