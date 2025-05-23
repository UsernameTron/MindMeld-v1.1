#!/usr/bin/env python3
"""
Behavior tests for the ExecutorAgent module.
"""

from unittest.mock import MagicMock, patch

import pytest

from packages.agents.claude_agents.agents.executor import ExecutorAgent
from packages.agents.claude_agents.api.client import ClaudeAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock Claude API client."""
    client = MagicMock(spec=ClaudeAPIClient)

    # Create a structured mock response
    mock_response = MagicMock()

    # Mock content list with text blocks
    mock_content = [
        MagicMock(
            type="text",
            text="""Here's a FastAPI authentication route implementation:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel

# Security settings
SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# User model
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # This would be replaced with actual user authentication
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

This implementation includes:
1. JWT token-based authentication
2. Password hashing with bcrypt
3. Token expiration
4. FastAPI OAuth2 integration

You would need to implement the `authenticate_user` function to check credentials against your database.""",
        )
    ]

    # Set up mock response attributes
    mock_response.content = mock_content
    mock_response.tool_calls = []

    # Configure the client to return the mock response
    client.send_message.return_value = mock_response
    client._call_claude = MagicMock(return_value=mock_response)

    return client


@pytest.fixture
def executor_agent(mock_api_client):
    """Create an executor agent with mock client."""
    return ExecutorAgent(
        api_client=mock_api_client,
        temperature=0.7,
    )


def test_executor_handles_task(executor_agent):
    """Test that executor agent properly processes tasks and returns formatted results."""
    # Task with ID for traceability
    task = {"id": "task_123", "description": "Generate FastAPI auth route"}

    response = executor_agent.process(task)

    # Verify response structure
    assert isinstance(response, dict)
    assert "task_id" in response
    assert response["task_id"] == "task_123"

    # Verify completion is present and is a string
    assert "completion" in response
    assert isinstance(response["completion"], str)

    # Check if code was included in the completion
    assert "FastAPI" in response["completion"]
    assert "def create_access_token" in response["completion"]
