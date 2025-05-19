from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from app.models.chat.chat import ChatCompletionResponse, ChatMessage
from app.services.errors import OpenAIServiceError
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def mock_chat_service():
    with patch("app.api.routes.chat.chat_service") as mock_service:
        yield mock_service


@pytest.fixture
def valid_api_key():
    return "valid-chat-key"


@pytest.fixture
def chat_request_payload():
    return {"messages": [{"role": "user", "content": "Hello"}], "temperature": 0.5}


def test_create_chat_completion_success(mock_chat_service, valid_api_key):
    mock_response = ChatCompletionResponse(
        message=ChatMessage(role="assistant", content="I'm an AI assistant."),
        model="gpt-4",
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    )
    # Fix the way we mock the async function
    mock_chat_service.generate_completion = AsyncMock(return_value=mock_response)
    # seed a valid API key with "chat" scope
    from app.services.auth.api_key_service import api_keys_db

    api_keys_db[valid_api_key] = {
        "client_id": "test",
        "scopes": ["chat"],
        "created_at": 0,
    }
    headers = {"X-API-Key": valid_api_key}
    response = client.post(
        "/chat/completion/",
        headers=headers,
        json={"messages": [{"role": "user", "content": "Hello"}], "temperature": 0.5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"]["role"] == "assistant"
    assert data["message"]["content"] == "I'm an AI assistant."
    assert data["model"] == "gpt-4"


def test_create_chat_completion_error(mock_chat_service, valid_api_key):
    mock_chat_service.generate_completion.side_effect = OpenAIServiceError("API Error")
    # seed a valid API key with "chat" scope
    from app.services.auth.api_key_service import api_keys_db

    api_keys_db[valid_api_key] = {
        "client_id": "test",
        "scopes": ["chat"],
        "created_at": 0,
    }
    headers = {"X-API-Key": valid_api_key}
    response = client.post(
        "/chat/completion/",
        headers=headers,
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 500
