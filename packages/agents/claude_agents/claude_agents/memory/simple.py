from typing import Dict, Any, Optional, List, Union, Tuple
import logging
import time
import uuid
from collections import OrderedDict

from .base import Memory

logger = logging.getLogger(__name__)

class SimpleMemory(Memory):
    """
    A simple in-memory storage system that maintains items in an ordered dictionary.
    Useful for short-term memory needs with basic recency-based retrieval.
    """
    
    def __init__(
        self,
        name: str = "simple_memory",
        max_items: int = 1000,
        ttl: Optional[int] = None,  # Time to live in seconds
    ):
        """
        Initialize the simple memory.
        
        Args:
            name: Name identifier for this memory
            max_items: Maximum number of items to store
            ttl: Optional time-to-live in seconds for items
        """
        super().__init__(name=name)
        self.max_items = max_items
        self.ttl = ttl
        self.items = OrderedDict()  # {item_id: (item, metadata, timestamp)}
    
    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an item to memory.
        
        Args:
            item: The item to store
            metadata: Optional metadata associated with the item
            
        Returns:
            ID of the stored item
        """
        # Generate ID if not in metadata
        item_id = metadata.get("id", str(uuid.uuid4())) if metadata else str(uuid.uuid4())
        
        # Add item
        timestamp = time.time()
        self.items[item_id] = (item, metadata or {}, timestamp)
        
        # Check if we need to remove older items
        self._enforce_limits()
        
        return item_id
    
    def get(self, item_id: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        """
        Retrieve an item from memory by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Tuple of (item, metadata) or (None, None) if not found
        """
        if item_id in self.items:
            item, metadata, timestamp = self.items[item_id]
            
            # Check if item has expired
            if self.ttl is not None and time.time() - timestamp > self.ttl:
                logger.debug(f"Item {item_id} has expired")
                self.remove(item_id)
                return None, None
            
            return item, metadata
        
        return None, None
    
    def search(self, query: Any, limit: int = 5) -> List[Tuple[str, Any, Optional[Dict[str, Any]], float]]:
        """
        Search memory for relevant items based on recency.
        Since this is a simple memory, it just returns the most recent items.
        
        Args:
            query: Ignored in SimpleMemory
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (item_id, item, metadata, recency_score)
        """
        # First clean up expired items
        self._remove_expired()
        
        # Return most recent items
        results = []
        items_list = list(self.items.items())
        
        # Sort by timestamp (most recent first)
        items_list.sort(key=lambda x: x[1][2], reverse=True)
        
        # Take only the limit number of items
        recent_items = items_list[:limit]
        
        # Format the results
        current_time = time.time()
        for item_id, (item, metadata, timestamp) in recent_items:
            # Calculate a recency score (1.0 = just added, 0.0 = oldest possible)
            if self.ttl:
                # Score based on TTL
                age = current_time - timestamp
                recency_score = max(0.0, 1.0 - (age / self.ttl))
            else:
                # Relative score based on oldest item
                if len(items_list) > 0:
                    oldest_timestamp = items_list[-1][1][2]
                    newest_timestamp = items_list[0][1][2]
                    if newest_timestamp == oldest_timestamp:
                        recency_score = 1.0
                    else:
                        recency_score = (timestamp - oldest_timestamp) / (newest_timestamp - oldest_timestamp)
                else:
                    recency_score = 1.0
            
            results.append((item_id, item, metadata, recency_score))
        
        return results
    
    def update(self, item_id: str, item: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing item in memory.
        
        Args:
            item_id: ID of the item to update
            item: Updated item
            metadata: Updated metadata
            
        Returns:
            True if successful, False otherwise
        """
        if item_id in self.items:
            _, existing_metadata, timestamp = self.items[item_id]
            
            # Merge metadata if provided
            if metadata:
                updated_metadata = existing_metadata.copy()
                updated_metadata.update(metadata)
            else:
                updated_metadata = existing_metadata
            
            # Update timestamp to current time
            self.items[item_id] = (item, updated_metadata, time.time())
            return True
        
        return False
    
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.
        
        Args:
            item_id: ID of the item to remove
            
        Returns:
            True if successful, False otherwise
        """
        if item_id in self.items:
            del self.items[item_id]
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all items from memory."""
        self.items.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary of statistics
        """
        # Clean up expired items first
        self._remove_expired()
        
        # Calculate stats
        current_time = time.time()
        timestamps = [timestamp for _, _, timestamp in self.items.values()]
        
        return {
            "name": self.name,
            "type": "simple",
            "item_count": len(self.items),
            "max_items": self.max_items,
            "ttl": self.ttl,
            "oldest_item_age": current_time - min(timestamps) if timestamps else 0,
            "newest_item_age": current_time - max(timestamps) if timestamps else 0,
            "average_item_age": current_time - (sum(timestamps) / len(timestamps)) if timestamps else 0,
        }
    
    def _enforce_limits(self) -> None:
        """Enforce maximum item limit by removing oldest items."""
        # First clean up expired items
        self._remove_expired()
        
        # Then enforce max items
        while len(self.items) > self.max_items:
            # Remove the oldest item (first added)
            self.items.popitem(last=False)
    
    def _remove_expired(self) -> None:
        """Remove items that have expired due to TTL."""
        if self.ttl is None:
            return
        
        current_time = time.time()
        expired_ids = [
            item_id
            for item_id, (_, _, timestamp) in self.items.items()
            if current_time - timestamp > self.ttl
        ]
        
        for item_id in expired_ids:
            logger.debug(f"Removing expired item {item_id}")
            del self.items[item_id]