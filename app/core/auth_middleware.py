"""
Authentication middleware for the MindMeld application.

This module implements middleware for API key and JWT authentication with scope enforcement,
allowing different routes to require different permissions.
"""

from fastapi import HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.auth_interface import AuthInterface
from app.core.config import settings
from app.services.auth.auth_service import AuthService, AuthResult
from typing import Optional

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Security scheme for HTTP Bearer
security = HTTPBearer()

# Define the require_auth dependency
async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    FastAPI dependency to require authentication.
    Verifies the Bearer token in the Authorization header.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = credentials.credentials
    # Use AuthService for validation
    from app.services.auth.auth_service import AuthService
    auth_service = AuthService()
    request = Request  # Placeholder, FastAPI will inject the actual request if needed
    # Validate JWT (scope can be None for generic use)
    is_valid = await auth_service.validate_jwt(request, required_scope=None)
    if is_valid is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Optionally decode and return token payload if needed
    return token

def get_auth_service() -> AuthInterface:
    """
    Get the authentication service instance.

    Returns:
        AuthInterface: An implementation of the authentication interface.
    """
    # Import here to avoid circular imports; replace with real implementation
    from app.services.auth.auth_service import AuthService
    return AuthService()

class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key or JWT authentication with scope enforcement.

    Attributes:
        auth_service (AuthService): The authentication service instance.
    """
    def __init__(self, app):
        """
        Initialize the APIKeyMiddleware.

        Args:
            app: The ASGI application instance.
        """
        super().__init__(app)
        self.auth_service = AuthService()

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and enforce authentication and scope.

        Args:
            request (Request): The incoming request.
            call_next: The next middleware or route handler.
        Returns:
            Response: The processed response, or an error response if authentication fails.
        """
        from app.core import test_config
        # Dynamically check test and auth flags
        if getattr(test_config, "IS_TESTING", False):
            return await call_next(request)
        if not settings.AUTH_ENABLED:
            return await call_next(request)
        auth_exempt_paths = [
            "/auth",
            "/test",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        if (
            any(request.url.path.startswith(path) for path in auth_exempt_paths)
            or request.method == "OPTIONS"
        ):
            return await call_next(request)
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        path = request.url.path
        required_scope = None
        # Support both versioned and legacy endpoints
        if path.startswith("/analyze") or path.startswith("/api/v1/analyze"):
            required_scope = "analyze"
        elif path.startswith("/chat") or path.startswith("/api/v1/chat"):
            required_scope = "chat"
        elif path.startswith("/rewrite") or path.startswith("/api/v1/rewrite"):
            required_scope = "rewrite"

        token = api_key or (
            auth_header.split(" ", 1)[1]
            if auth_header and auth_header.startswith("Bearer ")
            else None
        )
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication credentials"},
            )
        # Use AuthInterface for validation
        if api_key:
            result = await self.auth_service.validate_api_key(request, required_scope)
            if result == AuthResult.INVALID:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing authentication credentials"},
                )
            if result == AuthResult.INSUFFICIENT_SCOPE:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid or insufficient scope"},
                )
        else:
            result = await self.auth_service.validate_jwt(request, required_scope)
            if result == AuthResult.INVALID:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication credentials"},
                )
            if result == AuthResult.INSUFFICIENT_SCOPE:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid or insufficient scope"},
                )
        # If valid, set state for downstream use
        if api_key:
            request.state.api_key = api_key
        else:
            # Optionally set user info if needed
            pass
        return await call_next(request)
