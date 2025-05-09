from typing import Any, Dict, Optional

from pydantic import ConfigDict, Field

from app.models.common import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response model."""

    status: str = Field(
        "error",
        description="Status of the response",
        json_schema_extra={"example": "error"},
    )
    message: str = Field(
        ...,
        description="Error message",
        json_schema_extra={"example": "An error occurred"},
    )
    request_id: Optional[str] = Field(
        None,
        description="Request ID associated with the error",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    code: Optional[str] = Field(
        None,
        description="Error code",
        json_schema_extra={"example": "model_load_error"},
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
        json_schema_extra={"example": {"field": "value"}},
    )
    model_config = ConfigDict(extra="forbid")
