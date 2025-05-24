"""
Error handling utility for MindMeld.

This module provides a hierarchical exception system for all MindMeld operations,
enhanced error formatting, retry mechanisms, and transaction-like behavior.
"""

import functools
import logging
import os
import time
import traceback
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union

logger = logging.getLogger(__name__)

# Type variables for generic function types
T = TypeVar("T")
R = TypeVar("R")


class MindMeldError(Exception):
    """Base exception for all MindMeld-related errors."""

    def __init__(self, message: str, *args, **kwargs):
        """
        Initialize the exception.

        Args:
            message: Error message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.message = message
        super().__init__(message, *args, **kwargs)
        logger.error(f"{self.__class__.__name__}: {message}")


class ValidationError(MindMeldError):
    """Raised when input validation fails."""


class FileProcessingError(MindMeldError):
    """Raised when file operations fail."""


class LLMCallError(MindMeldError):
    """Raised when LLM call fails."""

    def __init__(self, message: str, model_name: Optional[str] = None, *args, **kwargs):
        """
        Initialize the exception.

        Args:
            message: Error message
            model_name: Name of the LLM model that failed
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.model_name = model_name
        if model_name:
            message = f"{message} (model: {model_name})"
        super().__init__(message, *args, **kwargs)


class ModelUnavailableError(LLMCallError):
    """Raised when required LLM model is not available."""


class AnalysisError(MindMeldError):
    """Raised when code analysis operations fail."""


class CompilationError(MindMeldError):
    """Raised when code compilation fails."""


class RepairError(MindMeldError):
    """Raised when code repair fails."""


class SchemaValidationError(MindMeldError):
    """Raised when output schema validation fails."""


class TimeoutError(MindMeldError):
    """Raised when an operation times out."""


class AgentExecutionError(MindMeldError):
    """Raised when agent execution fails."""

    def __init__(self, message: str, agent_name: Optional[str] = None, *args, **kwargs):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_name: Name of the agent that failed
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.agent_name = agent_name
        if agent_name:
            message = f"{message} (agent: {agent_name})"
        super().__init__(message, *args, **kwargs)


class TransactionError(MindMeldError):
    """Raised when a transaction fails."""


def format_error_for_json(error: Exception) -> dict:
    """
    Format an exception for inclusion in a JSON report.

    Args:
        error: The exception to format

    Returns:
        A dictionary containing error details
    """
    error_type = error.__class__.__name__
    error_message = str(error)

    result = {"message": error_message, "type": error_type}

    # Add stack trace in non-production environments
    if not is_production():
        result["traceback"] = traceback.format_exc()

    # Add additional context for specific error types
    if isinstance(error, LLMCallError) and error.model_name:
        result["model"] = error.model_name
    elif isinstance(error, AgentExecutionError) and error.agent_name:
        result["agent"] = error.agent_name

    return result


def is_production() -> bool:
    """
    Determine if we're running in a production environment.

    Returns:
        True if in production, False otherwise
    """
    return os.environ.get("MINDMELD_ENV", "").lower() == "production"


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    logger_func: Optional[Callable[[str], None]] = None,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Exception or tuple of exceptions to catch:
        logger_func: Function to use for logging

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            log = logger_func or (lambda msg: logger.warning(msg))
            retry_count = 0
            current_delay = delay

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        log(
                            f"Maximum retries ({max_retries}) reached for {func.__name__}. Last error: {str(e)}"
                        )
                        raise

                    log(
                        f"Retry {retry_count}/{max_retries} for {func.__name__} after error: {str(e)}. Waiting {current_delay:.2f}s"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

        return wrapper

    return decorator


def retry_on_llm_error(func: Callable[..., R]) -> Callable[..., R]:
    """
    Retry decorator specifically designed for LLM API calls.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        retries = 3
        delay = 2.0

        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(
                        f"LLM call failed (attempt {attempt+1}/{retries}): {str(e)}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    # On final attempt, wrap in LLMCallError
                    model = kwargs.get("model_name", "unknown")
                    raise LLMCallError(
                        f"LLM call failed after {retries} attempts: {str(e)}",
                        model_name=model,
                    )

        # This should never be reached, but just to be safe
        raise LLMCallError("Unexpected error in LLM retry logic")

    return wrapper


class Transaction:
    """
    Context manager for transaction-like behavior in critical operations.
    Provides rollback capabilities for file operations and other state changes.
    """

    def __init__(self, name: str = "unnamed_transaction"):
        """
        Initialize a new transaction.

        Args:
            name: Name of the transaction for logging
        """
        self.name = name
        self.operations = []
        self.completed = False

    def __enter__(self):
        """Enter the transaction context."""
        logger.debug(f"Starting transaction: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the transaction context.

        Rolls back on exception, otherwise marks as completed.
        """
        if exc_type is not None:
            logger.warning(f"Transaction {self.name} failed with error: {exc_val}")
            self.rollback()
            return False

        self.completed = True
        logger.debug(f"Transaction {self.name} completed successfully")
        return True

    def add_operation(
        self, operation_name: str, operation_data: Dict[str, Any] = None
    ) -> None:
        """
        Add an operation to the transaction.

        Args:
            operation_name: Name of the operation
            operation_data: Data associated with the operation
        """
        # TODO: Implement operation handling

    def add_file_write(self, file_path: str, backup_path: Optional[str] = None) -> None:
        """
        Add a file write operation to the transaction.

        Args:
            file_path: Path to the file being written
            backup_path: Path to backup of original file, if any
        """

        def undo_file_write():
            import os
            import shutil

            if backup_path and os.path.exists(backup_path):
                # Restore from backup
                shutil.copy2(backup_path, file_path)
                os.remove(backup_path)
            elif os.path.exists(file_path):
                # Just delete the file if there's no backup
                os.remove(file_path)

        self.add_operation(
            "file_write", undo_file_write, file_path=file_path, backup_path=backup_path
        )

    def rollback(self) -> None:
        """Roll back all operations in reverse order."""
        if self.completed:
            logger.warning(f"Cannot rollback completed transaction: {self.name}")
            return

        logger.info(f"Rolling back transaction: {self.name}")
        for operation in reversed(self.operations):
            try:
                operation["undo"]()
                logger.debug(
                    f"Rolled back {operation['type']} operation: {operation['metadata']}"
                )
            except Exception as e:
                logger.error(f"Error during rollback of {operation['type']}: {str(e)}")


def safe_file_write(file_path: str, content: str, use_transaction: bool = True) -> None:
    """
    Safely write content to a file with backup and rollback capabilities.

    Args:
        file_path: Path to write to
        content: Content to write
        use_transaction: Whether to use transaction for rollback capability
    """
    import os
    import shutil
    from pathlib import Path

    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    # Create backup if file exists
    backup_path = None
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)

    # Use transaction if requested
    if use_transaction:
        with Transaction(f"file_write_{Path(file_path).name}") as txn:
            if backup_path:
                txn.add_file_write(file_path, backup_path)

            # Write the file
            with open(file_path, "w") as f:
                f.write(content)
    else:
        # Just write the file without transaction
        with open(file_path, "w") as f:
            f.write(content)

        # Clean up backup on success
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
