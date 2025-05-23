import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..api.client import ClaudeAPIClient

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base agent class for different Claude-based reasoning agents."""

    def __init__(
        self,
        name: str,
        role: str,
        api_client: ClaudeAPIClient,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        Initialize the base agent.

        Args:
            name: Agent name (used for logging and identification)
            role: Role description of the agent
            api_client: Claude API client instance
            system_prompt: System prompt for the agent
            temperature: Temperature for responses (0-1)
            max_tokens: Maximum tokens in the response
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.api_client = api_client
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = []  # Will store message history

    def add_entry_to_history(self, entry_type: str, content: Any) -> None:
        """
        Add an entry to the agent's history.

        Args:
            entry_type: Type of entry (e.g., 'input', 'output')
            content: Content to store in history
        """
        self.history.append(
            {
                "type": entry_type,
                "content": content,
                "timestamp": str(uuid.uuid4()),  # Using UUID as a simple timestamp
            }
        )

    def _default_system_prompt(self) -> str:
        """Default system prompt based on agent role."""
        return f"You are {self.name}, an AI assistant specialized in {self.role}."

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        Process input data and produce output based on the agent's role.
        This should be implemented by concrete agent classes.

        Args:
            input_data: The input data for the agent to process

        Returns:
            Agent's processed output
        """
        pass

    def add_to_history(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the agent's conversation history.

        Args:
            message: Message object to add
        """
        self.history.append(message)

    def clear_history(self) -> None:
        """Clear the agent's conversation history."""
        self.history = []

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the agent's conversation history.

        Returns:
            List of message objects
        """
        return self.history

    def _call_claude(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        """
        Make a Claude API call with appropriate settings.

        Args:
            messages: List of message objects
            system: Optional system message (defaults to agent's system prompt)
            tools: Optional tool definitions

        Returns:
            Claude API response
        """
        system = system or self.system_prompt

        # Convert messages to the right format if needed
        api_messages = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                api_messages.append(msg)
            else:
                # Skip invalid messages
                continue

        response = self.api_client.send_message(
            messages=api_messages,
            system=system,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            tools=tools,
        )

        # Add to history if not in streaming mode
        # Extract content from response based on structure
        content_text = ""

        # Handle different response structures
        try:
            # Modern Anthropic API responses (Claude v0.7.0+)
            if hasattr(response, "content") and response.content:
                # The content is a list of content blocks (text, image, etc)
                for block in response.content:
                    # Only text blocks have text content we can extract
                    if hasattr(block, "type") and block.type == "text":
                        content_text = block.text
                        break
            # Handle dictionary-style responses
            elif isinstance(response, dict):
                if "content" in response:
                    for block in response.get("content", []):
                        if isinstance(block, dict) and block.get("type") == "text":
                            content_text = block.get("text", "")
                            break
                elif "completion" in response:
                    content_text = response["completion"]
        except (AttributeError, IndexError, KeyError) as e:
            logger.warning(f"Could not extract content from response: {e}")
            content_text = str(response)

        # Use the new add_to_history method signature
        self.add_to_history({"role": "assistant", "content": content_text})

        return response

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.role})"
