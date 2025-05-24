"""
Persona models for the MindMeld content transformation system.

This module defines the core schema for content transformation personas,
including their attributes, example pairs, and response structures.
"""

from typing import List, Optional

from pydantic import ConfigDict, Field

from app.models.common import BaseModel


class PersonaExample(BaseModel):
    """
    Example input/output pair for persona-based content transformation.

    Demonstrates expected transformation behavior for specific inputs.
    """

    input: str = Field(
        ...,
        description="Example input content",
        json_schema_extra={"example": "Rewrite this in a friendly tone."},
    )
    output: Optional[str] = Field(
        None,
        description="Example output after transformation",
        json_schema_extra={
            "example": "Sure thing! Here's your text in a friendly tone."
        },
    )
    model_config = ConfigDict(extra="forbid")


class PersonaDefinition(BaseModel):
    """
    Complete definition of a content transformation persona.

    Encapsulates identity, behavior, and examples for content rewriting.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the persona",
        json_schema_extra={"example": "cynical-humorist"},
    )
    name: str = Field(
        ...,
        description="Display name for the persona",
        json_schema_extra={"example": "Cynical Humorist"},
    )
    archetype: str = Field(
        ...,
        description="Short descriptor of the persona type",
        json_schema_extra={"example": "Satirist"},
    )
    description: str = Field(
        ...,
        description="Detailed description of the persona",
        json_schema_extra={
            "example": "A sardonic commentator who views everything with skepticism and dark humor."
        },
    )
    tone_instructions: str = Field(
        ...,
        description="Instructions for tone and voice",
        json_schema_extra={
            "example": "Write with dry wit, sarcasm, and pointed skepticism."
        },
    )
    system_prompt: Optional[str] = Field(
        None,
        description="Optional system prompt injection",
        json_schema_extra={
            "example": "As a cynical humorist, approach topics with skepticism and irony."
        },
    )
    examples: Optional[List[PersonaExample]] = Field(
        default=[],
        description="Example transformations",
        json_schema_extra={
            "example": [
                {
                    "input": "Rewrite this in a friendly tone.",
                    "output": "Sure thing! Here's your text in a friendly tone.",
                }
            ]
        },
    )
    model_config = ConfigDict(extra="forbid")


class PersonaListResponse(BaseModel):
    """Response model for listing available personas."""

    personas: List[PersonaDefinition] = Field(
        ...,
        description="Available personas",
        json_schema_extra={
            "example": [
                {
                    "id": "cynical-humorist",
                    "name": "Cynical Humorist",
                    "archetype": "Satirist",
                    "description": "A sardonic commentator who views everything with skepticism and dark humor.",
                    "tone_instructions": "Write with dry wit, sarcasm, and pointed skepticism.",
                    "system_prompt": "As a cynical humorist, approach topics with skepticism and irony.",
                    "examples": [
                        {
                            "input": "Rewrite this in a friendly tone.",
                            "output": "Sure thing! Here's your text in a friendly tone.",
                        }
                    ],
                }
            ]
        },
    )
    model_config = ConfigDict(extra="forbid")
