import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

import faiss
import numpy as np

from .base import Memory

logger = logging.getLogger(__name__)


class VectorMemory(Memory):
    """
    A vector-based memory system that stores embeddings for semantic search capabilities.
    Uses FAISS for efficient similarity search on embeddings.
    """

    def __init__(
        self,
        name: str = "vector_memory",
        embedding_fn: Callable[[Any], np.ndarray] = None,  # type: ignore
        embedding_dim: int = 768,
        max_items: int = 10000,
        index_type: str = "flat",
        ttl: Optional[int] = None,  # Time to live in seconds
    ):
        super().__init__(name=name)
        if embedding_fn is None:
            # Provide default embedding function returning zero vector
            self.embedding_fn = lambda x: np.zeros(embedding_dim, dtype=np.float32)
        else:
            self.embedding_fn = embedding_fn
        self.embedding_dim = embedding_dim
        self.max_items = max_items
        self.ttl = ttl

        # Initialize FAISS index
        if index_type == "flat":
            self.index = faiss.IndexFlatL2(embedding_dim)
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatL2(embedding_dim)
            train_data = np.zeros(
                (max(1, max_items // 10), embedding_dim), dtype=np.float32
            )
            self.index = faiss.IndexIVFFlat(
                quantizer, embedding_dim, min(100, max_items // 10)
            )
            self.index.train(n=train_data.shape[0], x=train_data)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")

        # Metadata storage
        self.items = {}  # {item_id: (item, metadata, timestamp)}
        self.id_to_idx = {}  # Map item_id to index in FAISS
        self.idx_to_id = {}  # Map index in FAISS to item_id
        self.next_idx = 0  # Next available index

        # For handling deletion and reindexing
        self.deleted_indices = set()

    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an item to memory with vector embedding.

        Args:
            item: The item to store
            metadata: Optional metadata associated with the item

        Returns:
            ID of the stored item
        """
        # Generate ID if not in metadata
        item_id = (
            metadata.get("id", str(uuid.uuid4())) if metadata else str(uuid.uuid4())
        )

        # Get embedding for the item
        embedding = self._get_embedding(item)

        # Store the item
        timestamp = time.time()
        self.items[item_id] = (item, metadata or {}, timestamp)

        # Add to FAISS index
        if len(self.deleted_indices) > 0:
            # Reuse a deleted index if available
            idx = self.deleted_indices.pop()
            self.index.remove_ids(np.array([idx], dtype=np.int64))
            self.index.add_with_ids(
                n=1,
                x=np.array([embedding], dtype=np.float32),
                xids=np.array([idx], dtype=np.int64),
            )
        else:
            # Use next available index
            idx = self.next_idx
            self.index.add_with_ids(
                n=1,
                x=np.array([embedding], dtype=np.float32),
                xids=np.array([idx], dtype=np.int64),
            )
            self.next_idx += 1

        # Update id mappings
        self.id_to_idx[item_id] = idx
        self.idx_to_id[idx] = item_id

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

    def search(
        self, query: Any, limit: int = 5
    ) -> List[Tuple[str, Any, Optional[Dict[str, Any]], float]]:
        """
        Search memory for semantically similar items.

        Args:
            query: Query to search for (will be converted to embedding)
            limit: Maximum number of results to return

        Returns:
            List of tuples (item_id, item, metadata, similarity_score)
        """
        # First clean up expired items
        self._remove_expired()

        # Get embedding for the query
        query_embedding = self._get_embedding(query)

        # Adjust limit to account for deleted items
        adjusted_limit = min(self.index.ntotal, limit + len(self.deleted_indices))

        # Search the FAISS index
        distances = np.empty((1, adjusted_limit), dtype=np.float32)
        labels = np.empty((1, adjusted_limit), dtype=np.int64)
        self.index.search(
            n=1,
            x=np.array([query_embedding], dtype=np.float32),
            k=adjusted_limit,
            distances=distances,
            labels=labels,
        )

        # Process results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], labels[0])):
            # Skip if index is invalid or if we've reached the actual limit
            if idx == -1 or len(results) >= limit:
                continue

            # Get item ID from index
            item_id = self.idx_to_id.get(int(idx))
            if not item_id or item_id not in self.items:
                continue

            # Get item and metadata
            item, metadata, _ = self.items[item_id]

            # Convert distance to similarity score (FAISS returns L2 distance)
            # Lower distance means higher similarity
            similarity_score = 1.0 / (1.0 + distance)

            results.append((item_id, item, metadata, similarity_score))

        return results

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
        if item_id not in self.items:
            return False

        # Get existing data
        _, existing_metadata, _ = self.items[item_id]

        # Merge metadata if provided
        if metadata:
            updated_metadata = existing_metadata.copy()
            updated_metadata.update(metadata)
        else:
            updated_metadata = existing_metadata

        # Update in storage
        timestamp = time.time()
        self.items[item_id] = (item, updated_metadata, timestamp)

        # Update in FAISS index
        idx = self.id_to_idx[item_id]
        embedding = self._get_embedding(item)

        # FAISS doesn't support direct updates, so we remove and add back
        self.index.remove_ids(np.array([idx], dtype=np.int64))
        self.index.add_with_ids(
            n=1,
            x=np.array([embedding], dtype=np.float32),
            xids=np.array([idx], dtype=np.int64),
        )

        return True

    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.

        Args:
            item_id: ID of the item to remove

        Returns:
            True if successful, False otherwise
        """
        if item_id not in self.items:
            return False

        # Get index for this item
        idx = self.id_to_idx[item_id]

        # Remove from FAISS
        self.index.remove_ids(np.array([idx], dtype=np.int64))

        # Mark index as deleted for future reuse
        self.deleted_indices.add(idx)

        # Clean up mappings
        del self.id_to_idx[item_id]
        del self.idx_to_id[idx]
        del self.items[item_id]

        return True

    def clear(self) -> None:
        """Clear all items from memory."""
        # Reset FAISS index
        self.embedding_dim
        self.index.reset()

        # Reset storage and mappings
        self.items.clear()
        self.id_to_idx.clear()
        self.idx_to_id.clear()
        self.deleted_indices.clear()
        self.next_idx = 0

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
            "type": "vector",
            "item_count": len(self.items),
            "index_size": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "max_items": self.max_items,
            "ttl": self.ttl,
            "oldest_item_age": current_time - min(timestamps) if timestamps else 0,
            "newest_item_age": current_time - max(timestamps) if timestamps else 0,
            "average_item_age": (
                current_time - (sum(timestamps) / len(timestamps)) if timestamps else 0
            ),
            "deleted_slots": len(self.deleted_indices),
        }

    def _get_embedding(self, item: Any) -> np.ndarray:
        """
        Get embedding vector for an item.

        Args:
            item: Item to embed

        Returns:
            Embedding vector
        """
        # self.embedding_fn is always set in __init__, so no need to check for None
        try:
            embedding = self.embedding_fn(item)

            # Ensure correct shape and type
            if isinstance(embedding, list):
                embedding = np.array(embedding, dtype=np.float32)

            if embedding.shape != (self.embedding_dim,):
                raise ValueError(
                    f"Embedding dimension mismatch: {embedding.shape} vs expected {(self.embedding_dim,)}"
                )

            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return a zero embedding as fallback
            return np.zeros(self.embedding_dim, dtype=np.float32)

    def _enforce_limits(self) -> None:
        """Enforce maximum item limit by removing oldest items."""
        # First clean up expired items
        self._remove_expired()

        # Then enforce max items
        if len(self.items) > self.max_items:
            # Find the oldest items
            items_by_age = sorted(
                [
                    (item_id, timestamp)
                    for item_id, (_, _, timestamp) in self.items.items()
                ],
                key=lambda x: x[1],
            )

            # Remove oldest items
            for item_id, _ in items_by_age[: len(self.items) - self.max_items]:
                self.remove(item_id)

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
            self.remove(item_id)
