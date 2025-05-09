from typing import List, Optional

from pydantic import ConfigDict, Field

from app.models.common import BaseModel


class Token(BaseModel):
    """Access and refresh token response model for authentication endpoints."""

    access_token: str = Field(
        ...,
        description="JWT access token",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )
    token_type: str = Field(
        "bearer", description="Token type", json_schema_extra={"example": "bearer"}
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )
    model_config = ConfigDict(extra="forbid")


class TokenData(BaseModel):
    """JWT token payload data, used for internal validation and scope checks."""

    username: Optional[str] = Field(
        None,
        description="Username from token subject",
        json_schema_extra={"example": "testuser"},
    )
    scopes: List[str] = Field(
        default_factory=list,
        description="List of scopes granted to the token",
        json_schema_extra={"example": ["analyze", "chat"]},
    )
    model_config = ConfigDict(extra="forbid")


class User(BaseModel):
    """User model for authentication and user info endpoints."""

    username: str = Field(
        ..., description="Unique username", json_schema_extra={"example": "testuser"}
    )
    email: Optional[str] = Field(
        None,
        description="User email",
        json_schema_extra={"example": "test@example.com"},
    )
    disabled: Optional[bool] = Field(
        False,
        description="Whether user is disabled",
        json_schema_extra={"example": False},
    )
    model_config = ConfigDict(extra="forbid")


class UserInDB(User):
    """User model with hashed password for storage (internal use only)."""

    hashed_password: str = Field(
        ...,
        description="Hashed password",
        json_schema_extra={"example": "$2b$12$KIXQ...hashed..."},
    )
    model_config = ConfigDict(extra="forbid")
