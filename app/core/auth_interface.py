"""
AuthInterface defines a contract for authentication logic in the MindMeld application.

This interface allows for pluggable authentication strategies, such as JWT and API key validation.
Implementations must provide async methods for both JWT and API key validation, enabling FastAPI
middleware and dependencies to use a consistent authentication pattern.

Usage:
    class MyAuthService(AuthInterface):
        async def validate_jwt(self, request: Request, required_scope: str = None):
            # Implement JWT validation logic
            ...
        async def validate_api_key(self, request: Request, required_scope: str = None):
            # Implement API key validation logic
            ...

This pattern enables dependency injection and easier testing/mocking of authentication logic.
"""
from abc import ABC, abstractmethod

from fastapi import Request


class AuthInterface(ABC):
    """
    Abstract base class for authentication logic in MindMeld.

    Implementations must provide async methods for JWT and API key validation.
    """
    @abstractmethod
    async def validate_jwt(self, request: Request, required_scope: str = None):
        """
        Validate a JWT from the incoming request.

        Args:
            request (Request): FastAPI Request object containing headers and context.
            required_scope (str, optional): Scope string to check for authorization.
        Returns:
            AuthResult or bool: Validation result (see implementation).
        """
        pass

    @abstractmethod
    async def validate_api_key(self, request: Request, required_scope: str = None):
        """
        Validate an API key from the incoming request.

        Args:
            request (Request): FastAPI Request object containing headers and context.
            required_scope (str, optional): Scope string to check for authorization.
        Returns:
            AuthResult or bool: Validation result (see implementation).
        """
        pass
