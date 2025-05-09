"""
Common service-level exceptions for the application.

This module defines base and specific exception classes for service-layer errors,
including validation, model inference, authentication, and external API issues.
"""

from typing import Any, Dict, List, Optional


class BaseServiceError(Exception):
    """
    Base exception for all service-related errors.

    Attributes:
        message (str): The error message.
        details (Optional[Dict[str, Any]]): Additional error details.
        resource_id (Optional[str]): Associated resource identifier, if any.
    """

    message: str
    details: Optional[Dict[str, Any]]
    resource_id: Optional[str]

    def __init__(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a BaseServiceError.

        Args:
            message (str): The error message.
            *args: Additional positional arguments (may include resource_id or details).
            **kwargs: Additional keyword arguments (may include details).
        """
        self.message = message
        self.args = (message,) + args
        self.details = None
        self.resource_id = None
        # Handle common patterns for details and resource_id
        if len(args) > 0 and isinstance(args[0], dict) and not kwargs.get("details"):
            self.details = args[0]
        elif len(args) > 1 and isinstance(args[1], dict) and not kwargs.get("details"):
            self.resource_id = args[0]
            self.details = args[1]
        else:
            self.details = kwargs.get("details")
            if args and not self.resource_id:
                self.resource_id = args[0]
        # Store all kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(message, *args)

    def __str__(self) -> str:
        """
        Return the error message as string.

        Returns:
            str: The error message.
        """
        return str(self.message)


ServiceError = BaseServiceError


class ValidationError(BaseServiceError):
    """Raised when input validation fails."""

    pass


class ModelLoadError(BaseServiceError):
    """Raised when a model fails to load."""

    pass


class ModelInferenceError(BaseServiceError):
    """Raised when model inference fails."""

    pass


class OpenAIError(BaseServiceError):
    """Raised when there's an issue with OpenAI API."""

    pass


class ExternalAPIError(BaseServiceError):
    """Raised when there's an issue with external API calls."""

    pass


class InferenceError(BaseServiceError):
    """Raised when model inference fails."""

    pass


class ResourceNotFoundError(BaseServiceError):
    """
    Raised when a requested resource is not found.

    Args:
        resource_type (str): The type of resource.
        resource_id (Optional[str]): The resource identifier.
        **kwargs: Additional keyword arguments.
    """

    def __init__(
        self, resource_type: str, resource_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Initialize a ResourceNotFoundError.

        Args:
            resource_type (str): The type of resource.
            resource_id (Optional[str]): The resource identifier.
            **kwargs: Additional keyword arguments.
        """
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, resource_id, **kwargs)


class AuthenticationError(BaseServiceError):
    """Raised when authentication fails."""

    pass


class RateLimitError(BaseServiceError):
    """Raised when a rate limit is exceeded."""

    pass


class InvalidTaskError(Exception):
    """
    Raised when an invalid task type is requested.

    Attributes:
        task (str): The invalid task name.
        valid_tasks (List[str]): List of valid task names.
    """

    task: str
    valid_tasks: List[str]

    def __init__(self, task: str, valid_tasks: Optional[List[str]] = None) -> None:
        """
        Initialize an InvalidTaskError.

        Args:
            task (str): The invalid task name.
            valid_tasks (Optional[List[str]]): List of valid task names.
        """
        self.task = task
        self.valid_tasks = valid_tasks or []
        message = f"Invalid task '{task}'"
        if valid_tasks:
            message += f". Valid tasks are: {', '.join(valid_tasks)}"
        super().__init__(message)


class ConfigurationError(ServiceError):
    """
    Error raised when there's a configuration issue.
    """
    pass


class OpenAIServiceError(ServiceError):
    """
    Error raised when there's an issue with OpenAI service.
    """
    pass
