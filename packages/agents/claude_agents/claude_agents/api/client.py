import os
import time
import logging
from typing import Dict, Any, Optional, List, Union

import anthropic
from anthropic import Anthropic
from anthropic.types import Message, MessageParam

logger = logging.getLogger(__name__)

class ClaudeAPIClient:
    """Client for interacting with the Claude API with built-in retry and error handling."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        max_retries: int = 5,
        backoff_factor: float = 1.5,
        max_tokens: int = 4096,
    ):
        """
        Initialize the Claude API client.
        
        Args:
            api_key: Claude API key (defaults to ANTHROPIC_API_KEY environment variable)
            model: Claude model to use
            max_retries: Maximum number of retries for failed API calls
            backoff_factor: Exponential backoff factor for retries
            max_tokens: Maximum number of tokens in the response
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as ANTHROPIC_API_KEY environment variable")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_tokens = max_tokens
        
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff time in seconds."""
        return min(60, self.backoff_factor ** attempt)
    
    def send_message(
        self, 
        messages: List[MessageParam],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Message:
        """
        Send a message to Claude with retry logic and error handling.
        
        Args:
            messages: List of message objects for the conversation
            system: System prompt for Claude
            max_tokens: Maximum number of tokens to generate (overrides default)
            temperature: Sampling temperature (0-1)
            tools: Optional list of tool definitions
            
        Returns:
            Claude API response
        """
        attempts = 0
        max_tokens = max_tokens or self.max_tokens
        
        while attempts < self.max_retries:
            try:
                # Prepare API call parameters
                params = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
                
                if system:
                    params["system"] = system
                    
                if tools:
                    params["tools"] = tools
                
                # Make the API call
                response = self.client.messages.create(**params)
                return response
                
            except anthropic.APIError as e:
                attempts += 1
                
                # Check if we should retry
                if attempts >= self.max_retries:
                    logger.error(f"Max retries exceeded. Last error: {str(e)}")
                    raise
                
                # Handle rate limiting specifically
                if e.status_code == 429:
                    backoff_time = self._exponential_backoff(attempts)
                    logger.warning(f"Rate limited. Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    continue
                    
                # Handle server errors (5xx)
                if e.status_code >= 500:
                    backoff_time = self._exponential_backoff(attempts)
                    logger.warning(f"Server error {e.status_code}. Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    continue
                
                # For other errors, raise immediately
                logger.error(f"API error: {str(e)}")
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
    
    def estimate_token_usage(self, text: str) -> int:
        """
        Estimate the number of tokens in the given text.
        This is a naive estimation used for monitoring purposes.
        
        Args:
            text: Text to estimate token count for
            
        Returns:
            Estimated token count
        """
        # Very rough estimation: ~4 characters per token on average
        return len(text) // 4
    
    def get_models(self) -> List[str]:
        """
        Get the list of available Claude models.
        
        Returns:
            List of available model IDs
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get models: {str(e)}")
            raise