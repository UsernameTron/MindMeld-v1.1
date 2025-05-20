import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class Agent(ABC):
    """Abstract base class for all agents in the system.

    This class defines the common interface and functionality that all
    agents in the MindMeld system should implement.
    """

    def __init__(self, name: Optional[str] = None, max_history_length: int = 100):
        """Initialize the agent with a name and history settings.

        Args:
            name: Custom name for the agent (defaults to class name)
            max_history_length: Maximum number of history entries to keep
        """
        self.name = name or self.__class__.__name__
        self.max_history_length = max_history_length
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.state = {}
        self.history = []
        self._initialize_state()

    def _initialize_state(self):
        """Initialize agent state with default values"""
        self.state = {
            "created_at": time.time(),
            "processed_count": 0,
            "last_processed": None,
        }

    def add_to_history(
        self, role: str, content: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.history.append(message)
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length :]

    def get_history(
        self, max_entries: Optional[int] = None, role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        filtered = self.history
        if role_filter:
            filtered = [msg for msg in filtered if msg["role"] == role_filter]
        if max_entries:
            filtered = filtered[-max_entries:]
        return filtered

    def clear_history(self) -> None:
        self.history = []

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Abstract processing interface for concrete agents."""
        pass

    def update_state(self, state_updates: Dict[str, Any]) -> None:
        self.state.update(state_updates)
