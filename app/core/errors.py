"""Error handling module for the MindMeld application.

This module defines custom exception handlers for various error types,
providing consistent error responses and logging.
"""

import traceback
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.models.common import StandardResponse
from app.models.error import ErrorResponse
from app.services.errors import (
    AuthenticationError,
    BaseServiceError,
    ExternalAPIError,
    InferenceError,
    InvalidTaskError,
    ModelInferenceError,
    ModelLoadError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
)

logger = get_logger()


async def service_error_handler(
    request: Request, exc: BaseServiceError
) -> JSONResponse:
    """
    Handle service-level exceptions and return a JSON response.

    Args:
        request (Request): The incoming request.
        exc (BaseServiceError): The service-level exception.
    Returns:
        JSONResponse: The error response.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "SERVICE_ERROR"

    # Map error types to status codes and codes (uppercase)
    if isinstance(exc, ModelLoadError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_code = "MODEL_LOAD_ERROR"
    elif isinstance(exc, ModelInferenceError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_code = "MODEL_INFERENCE_ERROR"
    elif isinstance(exc, InferenceError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "INFERENCE_ERROR"
    elif isinstance(exc, ExternalAPIError):
        status_code = status.HTTP_502_BAD_GATEWAY
        error_code = "EXTERNAL_API_ERROR"
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, ResourceNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = "RESOURCE_NOT_FOUND"
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
        error_code = "AUTHENTICATION_ERROR"
    elif isinstance(exc, RateLimitError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        error_code = "RATE_LIMIT_ERROR"

    request_id = getattr(request.state, "request_id", None)

    details = exc.details if isinstance(exc.details, dict) else {"value": exc.details}

    logger.error(f"{error_code}: {exc.message}", extra={"details": details})

    error_response: ErrorResponse = ErrorResponse(
        status="error",
        message=exc.message,
        request_id=request_id,
        code=error_code,
        details=details,
    )

    response = JSONResponse(
        status_code=status_code,
        content={
            **error_response.model_dump(),
            "detail": exc.message,
        },
    )

    # Make sure the attribute exists before accessing it
    if (
        isinstance(exc, RateLimitError)
        and hasattr(exc, "retry_after")
        and exc.retry_after
    ):
        response.headers["Retry-After"] = str(exc.retry_after)

    return response


async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Handle custom validation errors and return a JSON response.

    Args:
        request (Request): The incoming request.
        exc (ValidationError): The validation error exception.
    Returns:
        JSONResponse: The error response.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": exc.message,
            "details": exc.details if hasattr(exc, "details") else None,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors and return a StandardResponse.

    Args:
        request (Request): The incoming request.
        exc (RequestValidationError): The request validation error exception.
    Returns:
        JSONResponse: The error response.
    """
    errors = exc.errors()
    error_details = [
        {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        for error in errors
    ]
    error_response: StandardResponse[None] = StandardResponse(
        success=False,
        error="Validation error",
        code="VALIDATION_ERROR",
        meta={
            "details": error_details,
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def model_load_error_handler(
    request: Request, exc: ModelLoadError
) -> JSONResponse:
    """
    Handle model load errors and return a JSON response.

    Args:
        request (Request): The incoming request.
        exc (ModelLoadError): The model load error exception.
    Returns:
        JSONResponse: The error response.
    """
    error_response: StandardResponse[None] = StandardResponse(
        success=False,
        error=str(exc),
        code="MODEL_LOAD_ERROR",
        meta={
            "model_name": getattr(exc, "model_name", "unknown"),
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response.model_dump(),
    )


async def inference_error_handler(
    request: Request, exc: InferenceError
) -> JSONResponse:
    """
    Handle inference errors and return a JSON response.

    Args:
        request (Request): The incoming request.
        exc (InferenceError): The inference error exception.
    Returns:
        JSONResponse: The error response.
    """
    error_response: StandardResponse[None] = StandardResponse(
        success=False,
        error=str(exc),
        code="INFERENCE_ERROR",
        meta={"request_id": getattr(request.state, "request_id", "unknown")},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


async def invalid_task_error_handler(
    request: Request, exc: InvalidTaskError
) -> JSONResponse:
    """
    Handle invalid task errors and return a JSON response.

    Args:
        request (Request): The incoming request.
        exc (InvalidTaskError): The invalid task error exception.
    Returns:
        JSONResponse: The error response.
    """
    error_response: StandardResponse[None] = StandardResponse(
        success=False,
        error=str(exc),
        code="INVALID_TASK",
        meta={
            "task": getattr(exc, "task", "unknown"),
            "valid_tasks": getattr(exc, "valid_tasks", []),
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump()
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions and return a JSON response.

    Args:
        request (Request): The incoming request.
        exc (Exception): The unhandled exception.
    Returns:
        JSONResponse: The error response.
    """
    logger.error(
        f"UNHANDLED_EXCEPTION: {str(exc)}", extra={"traceback": traceback.format_exc()}
    )
    error_response: ErrorResponse = ErrorResponse(
        status="error",
        message="An unexpected error occurred.",
        request_id=getattr(request.state, "request_id", None),
        code="UNHANDLED_EXCEPTION",
        details={"exception": str(exc)},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> FastAPI:
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app (FastAPI): The FastAPI application instance.
    Returns:
        FastAPI: The app with handlers registered.
    """
    app.add_exception_handler(BaseServiceError, service_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(ModelLoadError, model_load_error_handler)
    app.add_exception_handler(InferenceError, inference_error_handler)
    app.add_exception_handler(InvalidTaskError, invalid_task_error_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    return app
