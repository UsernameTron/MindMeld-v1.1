from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Callable
import uuid
import logging

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
    ) -> Dict[str, Any]:
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
        
        response = self.api_client.send_message(
            messages=messages,
            system=system,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            tools=tools
        )
        
        # Add to history if not in streaming mode
        self.add_to_history({
            "role": "assistant",
            "content": response.content[0].text
        })
        
        return response
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.role})"