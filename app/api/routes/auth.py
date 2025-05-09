"""Authentication API routes for the MindMeld application.

This module defines FastAPI routes for user authentication, including
login, token refresh, and retrieving user information.
"""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.auth.auth import Token, User
from app.services.auth.auth_service import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    fake_users_db,
    get_current_active_user,
    get_user,
    verify_refresh_token,
)

router = APIRouter(
    tags=["auth"],
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """Get access token using username and password."""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        {"sub": user.username, "scopes": form_data.scopes}
    )
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str = Body(..., embed=True)) -> Token:
    """Obtain a new access token using a valid refresh token."""
    payload = verify_refresh_token(refresh_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    username = payload["sub"]
    user = get_user(fake_users_db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": payload.get("scopes", [])},
        expires_delta=access_token_expires,
    )
    # Always rotate refresh token for security
    new_refresh_token = create_refresh_token(
        {"sub": user.username, "scopes": payload.get("scopes", [])}
    )
    return Token(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Get authenticated user info."""
    return current_user
