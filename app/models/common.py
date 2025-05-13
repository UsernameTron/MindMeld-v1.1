"""Common models and utilities for the application."""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class BaseModel(PydanticBaseModel):
    """Base model with common functionality for all models in the application."""

    class Config:
        """Configuration for all models."""

        arbitrary_types_allowed = True
        populate_by_name = True


# Generic type for response data
T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response wrapper for consistent formatting."""

    success: bool = Field(
        ...,
        description="Whether the request was successful",
        json_schema_extra={"example": True},
    )
    data: Optional[T] = Field(
        None, description="Response data (only present on success)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message (only present on failure)",
        json_schema_extra={"example": "Something went wrong"},
    )
    code: Optional[str] = Field(
        None,
        description="Error code (only present on failure)",
        json_schema_extra={"example": "NOT_FOUND"},
    )
    request_id: Optional[str] = Field(None, description="Unique request ID for tracing")
    meta: Optional[Dict[str, Any]] = Field(
        default={},
        description="Metadata about the response",
        json_schema_extra={
            "example": {"version": "1.0", "details": {"source": "model"}}
        },
    )


class ErrorResponse(BaseModel):
    """Standard error response model for API errors."""
    detail: str = Field(..., description="Error message")
