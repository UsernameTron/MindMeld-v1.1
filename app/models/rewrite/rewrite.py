"""
Rewrite models for the MindMeld content transformation system.

This module defines the request and response schemas for the content
rewriting functionality, enabling persona-based content transformation.
"""

from typing import Optional

from app.models.common import BaseModel
from pydantic import ConfigDict, Field


class RewriteRequest(BaseModel):
    """
    Request model for content rewriting operations.
    """

    content: str = Field(
        ...,
        description="Content to be rewritten",
        json_schema_extra={"example": "Rewrite this in a more formal tone."},
    )
    persona_id: str = Field(
        ...,
        description="ID of the persona to apply",
        json_schema_extra={"example": "cynical-humorist"},
    )
    content_type: Optional[str] = Field(
        "general",
        description="Type of content being rewritten",
        json_schema_extra={"example": "general"},
    )
    temperature: Optional[float] = Field(
        0.7,
        description="Controls randomness in generation",
        ge=0.0,
        le=2.0,
        json_schema_extra={"example": 0.7},
    )
    model_config = ConfigDict(extra="forbid")


class RewriteResponse(BaseModel):
    """
    Response model for content rewriting operations.
    """

    original_content: str = Field(
        ...,
        description="Original input content",
        json_schema_extra={"example": "Rewrite this in a more formal tone."},
    )
    rewritten_content: str = Field(
        ...,
        description="Rewritten content with persona applied",
        json_schema_extra={
            "example": "Kindly rephrase the following in a more formal manner."
        },
    )
    persona_id: str = Field(
        ...,
        description="ID of the persona that was applied",
        json_schema_extra={"example": "cynical-humorist"},
    )
    persona_name: str = Field(
        ...,
        description="Name of the persona that was applied",
        json_schema_extra={"example": "Cynical Humorist"},
    )
    model_config = ConfigDict(extra="forbid")
