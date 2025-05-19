"""
Chat models for the MindMeld backend.

This module defines the schema for chat interactions including
message structure, completion requests, and response formats.
"""

from typing import Dict, List, Literal, Optional

from app.models.common import BaseModel
from pydantic import ConfigDict, Field


class ChatMessage(BaseModel):
    """Single message in a chat conversation from a specific role."""

    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="The role of the message sender",
        json_schema_extra={"example": "user"},
    )
    content: str = Field(
        ...,
        description="The content of the message",
        json_schema_extra={"example": "Tell me about machine learning."},
    )
    model_config = ConfigDict(extra="forbid")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completion operations."""

    messages: List[ChatMessage] = Field(
        ...,
        description="List of messages comprising the conversation",
        min_length=1,
        json_schema_extra={
            "example": [{"role": "user", "content": "Tell me about machine learning."}]
        },
    )
    model: Optional[str] = Field(
        None,
        description="Model to use for completion",
        json_schema_extra={"example": "gpt-4"},
    )
    temperature: Optional[float] = Field(
        0.7,
        description="Controls randomness in completions",
        ge=0.0,
        le=2.0,
        json_schema_extra={"example": 0.7},
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum tokens to generate",
        gt=0,
        json_schema_extra={"example": 1000},
    )
    model_config = ConfigDict(extra="forbid")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completion operations."""

    message: ChatMessage = Field(
        ...,
        description="The response message from the assistant",
        json_schema_extra={
            "example": {
                "role": "assistant",
                "content": "Machine learning is a field of AI...",
            }
        },
    )
    model: str = Field(
        ...,
        description="The model used for completion",
        json_schema_extra={"example": "gpt-4"},
    )
    usage: Dict[str, int] = Field(
        ...,
        description="Token usage information",
        json_schema_extra={
            "example": {
                "prompt_tokens": 12,
                "completion_tokens": 24,
                "total_tokens": 36,
            }
        },
    )
    model_config = ConfigDict(extra="forbid")
