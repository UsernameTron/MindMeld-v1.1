from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.chat.chat import ChatCompletionRequest, ChatMessage
from app.services.chat.chat_service import ChatService, OpenAIServiceError


@pytest.fixture
def mock_chat_service():
    """Create a fresh ChatService with mocked client for testing."""
    service = ChatService()
    # Replace the real client with a mock
    service.client = MagicMock()
    service.client.chat.completions.create = AsyncMock()
    return service


@pytest.fixture
def sample_request():
    """Sample request for testing."""
    return ChatCompletionRequest(messages=[ChatMessage(role="user", content="Hello")])


@pytest.mark.asyncio
async def test_generate_completion_success(mock_chat_service, sample_request):
    """Test successful completion generation."""
    # Create mock response
    mock_response = MagicMock()
    mock_response.model = "gpt-4"
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello, how can I help you?"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 8
    mock_response.usage.total_tokens = 18

    # Set up the mock to return our response
    mock_chat_service.client.chat.completions.create.return_value = mock_response

    # Call the method
    response = await mock_chat_service.generate_completion(sample_request)

    # Verify the response
    assert response.message.role == "assistant"
    assert response.message.content == "Hello, how can I help you?"
    assert response.model == "gpt-4"
    assert response.usage["total_tokens"] == 18


@pytest.mark.asyncio
async def test_generate_completion_error(mock_chat_service, sample_request):
    """Test error handling in completion generation."""
    # Set up the mock to raise an exception
    mock_chat_service.client.chat.completions.create.side_effect = Exception(
        "API Error"
    )

    # Verify the error is properly handled
    with pytest.raises(OpenAIServiceError):
        await mock_chat_service.generate_completion(sample_request)


# Add a few simple validation tests
def test_pydantic_validation_empty_messages():
    """Test validation for empty messages list."""
    with pytest.raises(Exception):  # Any validation exception
        ChatCompletionRequest(messages=[])


def test_pydantic_validation_invalid_temperature():
    """Test validation for invalid temperature."""
    with pytest.raises(Exception):  # Any validation exception
        ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=3.0,  # Too high
        )
