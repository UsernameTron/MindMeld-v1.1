from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.rewrite.rewrite import RewriteRequest
from app.services.errors import OpenAIServiceError
from app.services.rewrite.rewrite_service import RewriteService


@pytest.mark.asyncio
@patch("app.services.rewrite.rewrite_service.persona_service")
@patch("app.services.rewrite.rewrite_service.chat_service")
async def test_rewrite_content_success(mock_chat_service, mock_persona_service):
    # Mock persona
    persona = MagicMock()
    persona.id = "cynical-humorist"
    persona.name = "Cynical Humorist"
    persona.archetype = "Satirist"
    persona.tone_instructions = "Test"
    persona.system_prompt = "Test"
    persona.examples = []
    mock_persona_service.get_persona.return_value = persona

    # Mock chat service
    mock_chat_service.generate_completion = AsyncMock()
    mock_chat_service.generate_completion.return_value.message.content = "Rewritten!"

    req = RewriteRequest(content="Hello", persona_id="cynical-humorist")
    service = RewriteService()
    result = await service.rewrite_content(req)
    assert result.rewritten_content == "Rewritten!"
    assert result.persona_id == "cynical-humorist"


@pytest.mark.asyncio
@patch("app.services.rewrite.rewrite_service.persona_service")
@patch("app.services.rewrite.rewrite_service.chat_service")
async def test_rewrite_temperature_variation(mock_chat_service, mock_persona_service):
    """Test that temperature parameter is correctly passed to the chat service."""
    mock_persona = MagicMock()
    mock_persona.id = "test-persona"
    mock_persona.name = "Test Persona"
    mock_persona_service.get_persona.return_value = mock_persona
    mock_chat_service.generate_completion = AsyncMock()
    mock_chat_service.generate_completion.return_value.message.content = (
        "Rewritten content"
    )
    service = RewriteService()
    request = RewriteRequest(
        content="Original content", persona_id="test-persona", temperature=0.2
    )
    await service.rewrite_content(request)
    args, kwargs = mock_chat_service.generate_completion.call_args
    chat_request = args[0]
    assert chat_request.temperature == 0.2


@pytest.mark.asyncio
@patch("app.services.rewrite.rewrite_service.persona_service")
@patch("app.services.rewrite.rewrite_service.chat_service")
async def test_rewrite_error_handling(mock_chat_service, mock_persona_service):
    """Test that errors from the chat service are properly handled."""
    mock_persona = MagicMock()
    mock_persona.id = "test-persona"
    mock_persona_service.get_persona.return_value = mock_persona
    mock_chat_service.generate_completion = AsyncMock(
        side_effect=Exception("API error")
    )
    service = RewriteService()
    request = RewriteRequest(content="Original content", persona_id="test-persona")
    with pytest.raises(OpenAIServiceError):
        await service.rewrite_content(request)
