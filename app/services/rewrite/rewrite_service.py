"""
Rewrite service module for the MindMeld backend.

This module provides content transformation functionality using personas.
It connects the persona service with the chat service to rewrite content
according to specific persona characteristics and styles.
"""

import logging
from typing import Dict, List

from app.models.chat.chat import ChatCompletionRequest, ChatMessage
from app.models.rewrite.rewrite import RewriteRequest, RewriteResponse
from app.services.chat.chat_service import chat_service
from app.services.errors import OpenAIServiceError, ResourceNotFoundError
from app.services.persona.persona_service import persona_service

logger = logging.getLogger(__name__)


class RewriteService:
    """
    Service for rewriting content using personas.

    Transforms input content according to persona definitions,
    leveraging the chat service for actual content generation
    and the persona service for persona characteristics.
    """

    def _construct_prompt(self, request: RewriteRequest) -> List[Dict[str, str]]:
        """
        Construct prompt for the rewrite operation.

        Args:
            request: RewriteRequest containing content and persona ID

        Returns:
            List of message dictionaries to send to the chat service

        Raises:
            ResourceNotFoundError: If the requested persona is not found
        """
        # Get the persona definition
        try:
            persona = persona_service.get_persona(request.persona_id)
        except ResourceNotFoundError as e:
            logger.error(f"Persona not found: {request.persona_id}")
            raise e
        # Construct messages array
        messages = []
        # Add system prompt
        system_prompt = f"""You are a content rewriter that transforms text using a specific persona.\n\nPersona: {persona.name} ({persona.archetype})\nTone Instructions: {persona.tone_instructions}\n"""
        # Add persona's system prompt if available
        if persona.system_prompt:
            system_prompt += f"\n{persona.system_prompt}"
        # Add content type instructions
        if request.content_type:
            system_prompt += f"\nYou are rewriting {request.content_type} content."
        messages.append({"role": "system", "content": system_prompt})
        # Add examples if available
        if persona.examples:
            for example in persona.examples:
                messages.append({"role": "user", "content": example.input})
                if example.output:  # Only add if output exists
                    messages.append({"role": "assistant", "content": example.output})
        # Add the actual request
        messages.append(
            {
                "role": "user",
                "content": f"Please rewrite the following content using the {persona.name} persona:\n\n{request.content}",
            }
        )
        return messages

    async def rewrite_content(self, request: RewriteRequest) -> RewriteResponse:
        """
        Rewrite content using the specified persona.

        Args:
            request: RewriteRequest containing content and persona_id

        Returns:
            RewriteResponse with the original and rewritten content

        Raises:
            ResourceNotFoundError: If the persona doesn't exist
            OpenAIServiceError: If there's an error with the OpenAI API
        """
        try:
            # Get the persona for response metadata
            persona = persona_service.get_persona(request.persona_id)
            # Construct messages for the chat completion
            prompt_messages = self._construct_prompt(request)
            # Convert to ChatMessage objects
            chat_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in prompt_messages
            ]
            # Create chat request
            chat_request = ChatCompletionRequest(
                messages=chat_messages,
                temperature=request.temperature,
            )
            # Get completion from chat service
            logger.info(f"Sending rewrite request for persona: {persona.id}")
            chat_response = await chat_service.generate_completion(chat_request)
            # Create response object
            result = RewriteResponse(
                original_content=request.content,
                rewritten_content=chat_response.message.content,
                persona_id=persona.id,
                persona_name=persona.name,
            )
            return result
        except Exception as e:
            logger.error(f"Error in rewrite service: {str(e)}")
            raise OpenAIServiceError(f"Error rewriting content: {str(e)}")


# Create service instance
rewrite_service = RewriteService()
