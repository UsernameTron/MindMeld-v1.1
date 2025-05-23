import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Memory(ABC):
    """Base abstract class for all memory systems."""

    def __init__(self, name: str = "memory"):
        """
        Initialize the memory system.

        Args:
            name: Name identifier for this memory system
        """
        self.name = name
        self.id = str(uuid.uuid4())

    @abstractmethod
    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an item to memory.

        Args:
            item: The item to store
            metadata: Optional metadata associated with the item

        Returns:
            ID of the stored item
        """
        pass

    @abstractmethod
    def get(self, item_id: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        """
        Retrieve an item from memory by ID.

        Args:
            item_id: ID of the item to retrieve

        Returns:
            Tuple of (item, metadata) or (None, None) if not found
        """
        pass

    @abstractmethod
    def search(
        self, query: Any, limit: int = 5
    ) -> List[Tuple[str, Any, Optional[Dict[str, Any]], float]]:
        """
        Search memory for relevant items.

        Args:
            query: Search query (implementation-specific)
            limit: Maximum number of results to return

        Returns:
            List of tuples (item_id, item, metadata, relevance_score)
        """
        pass

    @abstractmethod
    def update(
        self, item_id: str, item: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing item in memory.

        Args:
            item_id: ID of the item to update
            item: Updated item
            metadata: Updated metadata

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.

        Args:
            item_id: ID of the item to remove

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all items from memory."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.

        Returns:
            Dictionary of statistics
        """
        pass
