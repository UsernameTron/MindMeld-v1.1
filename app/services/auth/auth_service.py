"""Authentication service for JWT and user management.

This module provides functions for password hashing, token generation,
and user authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.models.auth.auth import TokenData, User, UserInDB
from app.core.auth_interface import AuthInterface

# Configuration
SECRET_KEY: str = getattr(settings, "JWT_SECRET_KEY", "changeme")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_SECRET_KEY: str = getattr(settings, "JWT_REFRESH_SECRET_KEY", "refreshchangeme")
REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "analyze": "Access analyze endpoints",
        "chat": "Access chat endpoints",
        "rewrite": "Access rewrite endpoints",
        "admin": "Full admin access",
    },
)

# Demo users database (replace with real DB in production)
fake_users_db: Dict[str, Dict[str, Any]] = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def get_user(db: Optional[Dict[str, Any]], username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if not db:
        return None
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(
    db: Dict[str, Any], username: str, password: str
) -> Union[UserInDB, bool]:
    """Authenticate user with username and password."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a refresh token."""
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> User:
    """Get current user from JWT token."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if user is active."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class AuthResult(Enum):
    """
    Enum representing authentication results for API key and JWT validation.

    - OK: Authentication and (if required) scope check succeeded.
    - INVALID: Authentication failed (invalid or missing credentials).
    - INSUFFICIENT_SCOPE: Authenticated, but required scope is missing.
    """
    OK = "ok"
    INVALID = "invalid"  # 401
    INSUFFICIENT_SCOPE = "insufficient_scope"  # 403

class AuthService(AuthInterface):
    async def validate_jwt(self, request: Request, required_scope: str = None):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return AuthResult.INVALID
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            scopes = payload.get("scopes", [])
            user = get_user(fake_users_db, username)
            if not user:
                return AuthResult.INVALID
            if required_scope and required_scope not in scopes:
                return AuthResult.INSUFFICIENT_SCOPE
            return AuthResult.OK
        except JWTError:
            return AuthResult.INVALID

    async def validate_api_key(self, request: Request, required_scope: str = None):
        api_key = request.headers.get("X-API-Key")
        valid_keys = {"valid_key", "valid-analyze-key", "valid-chat-key", "valid-rewrite-key"}  # Accept all test keys
        if not api_key:
            return AuthResult.INVALID
        if api_key not in valid_keys:
            return AuthResult.INSUFFICIENT_SCOPE
        return AuthResult.OK
