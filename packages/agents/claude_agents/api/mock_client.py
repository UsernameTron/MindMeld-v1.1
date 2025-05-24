"""
Mock API client for testing Agent implementations.
"""

from typing import Any, Dict, List, Optional


class MockAPIResponse:
    """Mock response from API."""

    def __init__(self, content: str):
        """Initialize the mock response."""
        self.content = [type("Content", (), {"text": content})]
        self.model = "claude-3-mock-model"
        self.id = "mock-response-id-123456"
        self.type = "message"
        self.role = "assistant"


class MockClaudeAPIClient:
    """Mock Claude API client for testing."""

    def __init__(
        self,
        api_key: Optional[str] = "mock_key",
        model: str = "claude-3-mock-20240229",
        max_retries: int = 5,
        backoff_factor: float = 1.5,
        max_tokens: int = 4096,
    ):
        """Initialize the mock API client with the same interface as ClaudeAPIClient."""
        self.api_key = api_key or "mock_key_default"
        self.model = model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_tokens = max_tokens

    def send_message(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> MockAPIResponse:
        """
        Mock sending a message to the Claude API.

        Args:
            messages: List of message objects with role and content
            system: Optional system prompt
            max_tokens: Maximum number of tokens in the response
            temperature: Temperature parameter for response generation
            tools: Optional list of tools to make available

        Returns:
            MockAPIResponse: A mock API response
        """
        # If there are tools provided, provide a mock tool use response
        if tools:
            return MockAPIResponse("I'll use a tool to help with this request.")

        # Get the last user message for context in our mock response
        last_message = messages[-1] if messages else {"role": "user", "content": ""}
        if last_message.get("role") == "user":
            user_content = last_message.get("content", "")
            # Generate a slightly more relevant mock response based on content length
            if len(str(user_content)) > 100:
                return MockAPIResponse(
                    f"This is a detailed mock response to your request about {user_content[:20]}..."
                )

        return MockAPIResponse("This is a mock response from Claude API.")
