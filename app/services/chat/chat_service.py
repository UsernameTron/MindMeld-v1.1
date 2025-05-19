"""
Chat service module for the MindMeld backend.

This module provides service functionality for chat completions
using OpenAI's API. It handles request preparation, API interaction,
and response processing for chat-based operations.
"""

import logging
from typing import Any, Dict

from app.core.config import settings
from app.models.chat.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)
from app.services.errors import ConfigurationError, ServiceError
from openai import AsyncOpenAI
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class OpenAIServiceError(ServiceError):
    """Error raised when there's an issue with OpenAI service interactions."""

    pass


class ChatService:
    """
    Service for handling chat completions via OpenAI API.

    Provides functionality to generate text completions using OpenAI's
    chat models, with configurable parameters and error handling.
    """

    def __init__(self) -> None:
        """
        Initialize the ChatService with OpenAI credentials.

        Raises:
            ConfigurationError: If OpenAI API key is missing
        """
        # Validate configuration first
        if not settings.openai_api_key:
            raise ConfigurationError("OpenAI API key not found in environment")
        self.api_key = settings.openai_api_key
        self.default_model = settings.OPENAI_MODEL
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Generate a chat completion using OpenAI API.

        Args:
            request: The ChatCompletionRequest containing messages and parameters

        Returns:
            ChatCompletionResponse with the assistant's reply

        Raises:
            OpenAIServiceError: If there's an error with the OpenAI API
        """
        with tracer.start_as_current_span("generate_completion"):
            try:
                model = request.model or self.default_model
                openai_messages = [
                    {"role": msg.role, "content": msg.content} for msg in request.messages
                ]
                params: Dict[str, Any] = {
                    "model": model,
                    "messages": openai_messages,
                    "temperature": request.temperature,
                }
                if request.max_tokens:
                    params["max_tokens"] = request.max_tokens
                logger.debug(f"Sending request to OpenAI API with model: {model}")
                response = await self.client.chat.completions.create(**params)
                assistant_message = ChatMessage(
                    role="assistant", content=response.choices[0].message.content
                )
                return ChatCompletionResponse(
                    message=assistant_message,
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                )
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                raise OpenAIServiceError(f"Error from OpenAI: {str(e)}")


# Create service instance
chat_service = ChatService()
