import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ...ai.client import BaseLLMClient, LLMClientFactory
from ...ai.embeddings import EmbeddingService
from ..core.base import Agent


@dataclass
class MemoryEntry:
    """A single memory entry with content and metadata"""

    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0


class VectorMemoryException(Exception):
    """Base exception class for VectorMemoryAgent errors"""

    pass


class VectorStorageError(VectorMemoryException):
    """Exception raised when vector storage operations fail"""

    pass


class VectorMemoryAgent(Agent):
    """Agent for semantic memory storage and retrieval using vector embeddings"""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None,
        llm_client: Optional[BaseLLMClient] = None,
        index_name: str = "default",
        similarity_threshold: float = 0.7,
    ):
        """Initialize the vector memory agent

        Args:
            storage_path: Path to store vector database
            embedding_service: Service for generating embeddings
            llm_client: LLM client for text generation
            index_name: Name of the vector index
            similarity_threshold: Threshold for similarity search
        """
        super().__init__(name="vector_memory")

        self.storage_path = storage_path or os.path.join(
            os.getcwd(), "data", "storage", "vector_memory"
        )
        self.embedding_service = embedding_service or EmbeddingService()
        self.llm_client = llm_client or LLMClientFactory.create_client()
        self.index_name = index_name
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(__name__)

        # In-memory storage as a simple fallback if vector DB isn't available
        self._memory_entries: Dict[str, MemoryEntry] = {}

        # Initialize vector store
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize the vector storage backend"""
        try:
            # Ensure storage directory exists
            os.makedirs(self.storage_path, exist_ok=True)

            # Attempt to load existing memories
            self._load_memories()

            self.logger.info(f"Vector memory initialized at: {self.storage_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize vector storage: {str(e)}")
            self.logger.warning("Falling back to in-memory storage")

    def _load_memories(self):
        """Load memories from disk"""
        index_path = os.path.join(self.storage_path, f"{self.index_name}.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r") as f:
                    entries_data = json.load(f)

                for entry_data in entries_data:
                    entry = MemoryEntry(
                        content=entry_data["content"],
                        embedding=entry_data["embedding"],
                        metadata=entry_data.get("metadata", {}),
                        entry_id=entry_data["entry_id"],
                        created_at=entry_data.get("created_at", time.time()),
                        last_accessed=entry_data.get("last_accessed", time.time()),
                        access_count=entry_data.get("access_count", 0),
                    )
                    self._memory_entries[entry.entry_id] = entry

                self.logger.info(
                    f"Loaded {len(self._memory_entries)} memories from {index_path}"
                )
            except Exception as e:
                self.logger.error(f"Failed to load memories: {str(e)}")
                raise VectorStorageError(f"Failed to load memories: {str(e)}") from e

    def _save_memories(self):
        """Save memories to disk"""
        index_path = os.path.join(self.storage_path, f"{self.index_name}.json")
        try:
            entries_data = []
            for entry in self._memory_entries.values():
                entries_data.append(
                    {
                        "content": entry.content,
                        "embedding": entry.embedding,
                        "metadata": entry.metadata,
                        "entry_id": entry.entry_id,
                        "created_at": entry.created_at,
                        "last_accessed": entry.last_accessed,
                        "access_count": entry.access_count,
                    }
                )

            with open(index_path, "w") as f:
                json.dump(entries_data, f)

            self.logger.debug(f"Saved {len(entries_data)} memories to {index_path}")
        except Exception as e:
            self.logger.error(f"Failed to save memories: {str(e)}")
            raise VectorStorageError(f"Failed to save memories: {str(e)}") from e

    def add_memory(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a new memory to storage

        Args:
            content: Text content to store
            metadata: Additional metadata about the content

        Returns:
            ID of the stored memory entry
        """
        try:
            # Generate embedding
            embedding_result = self.embedding_service.get_embedding(content, metadata)

            # Create memory entry
            entry = MemoryEntry(
                content=content,
                embedding=embedding_result.vector,
                metadata=metadata or {},
            )

            # Store entry
            self._memory_entries[entry.entry_id] = entry

            # Save to disk
            self._save_memories()

            self.logger.info(f"Memory entry added with ID: {entry.entry_id}")
            return entry.entry_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {str(e)}")
            raise VectorMemoryException(f"Failed to add memory: {str(e)}") from e

    def batch_add_memories(
        self, contents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Add multiple memories at once for better performance

        Args:
            contents: List of text contents to store
            metadatas: List of metadata dictionaries, one per content

        Returns:
            List of entry IDs for the stored memories
        """
        if metadatas is None:
            metadatas = [{}] * len(contents)

        entry_ids = []
        for content, metadata in zip(contents, metadatas):
            entry_id = self.add_memory(content, metadata)
            entry_ids.append(entry_id)

        return entry_ids

    def get_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID

        Args:
            entry_id: ID of the memory to retrieve

        Returns:
            Memory entry or None if not found
        """
        entry = self._memory_entries.get(entry_id)
        if entry:
            # Update access stats
            entry.last_accessed = time.time()
            entry.access_count += 1
            return entry
        return None

    def search_memories(
        self, query: str, limit: int = 5
    ) -> List[Tuple[MemoryEntry, float]]:
        """Search for memories similar to the query

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of memory entries with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.get_embedding(query)

            # Calculate similarities
            results = []
            for entry in self._memory_entries.values():
                similarity = self.embedding_service.compute_similarity(
                    query_embedding.vector, entry.embedding
                )

                if similarity >= self.similarity_threshold:
                    results.append((entry, similarity))

            # Sort by similarity (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            # Update access stats for retrieved memories
            for entry, _ in results[:limit]:
                entry.last_accessed = time.time()
                entry.access_count += 1

            return results[:limit]
        except Exception as e:
            self.logger.error(f"Memory search failed: {str(e)}")
            raise VectorMemoryException(f"Memory search failed: {str(e)}") from e

    def delete_memory(self, entry_id: str) -> bool:
        """Delete a memory by ID

        Args:
            entry_id: ID of the memory to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            if entry_id in self._memory_entries:
                del self._memory_entries[entry_id]
                self._save_memories()
                return True
            return False
        except Exception as e:
            raise VectorStorageError(f"Failed to delete memory: {str(e)}") from e

    def clear_memories(self) -> int:
        """Clear all memories

        Returns:
            Number of memories cleared
        """
        count = len(self._memory_entries)
        self._memory_entries.clear()
        self._save_memories()
        return count

    def update_memory(
        self,
        entry_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update a memory entry

        Args:
            entry_id: ID of the memory to update
            content: New content (if None, keep existing)
            metadata: Metadata to update (if None, keep existing)

        Returns:
            True if updated, False if not found
        """
        entry = self._memory_entries.get(entry_id)
        if not entry:
            return False

        # Update content and regenerate embedding if provided
        if content is not None and content != entry.content:
            embedding_result = self.embedding_service.get_embedding(content)
            entry.content = content
            entry.embedding = embedding_result.vector

        # Update metadata if provided
        if metadata is not None:
            entry.metadata = {**entry.metadata, **metadata}

        # Update timestamp
        entry.last_accessed = time.time()

        # Save changes
        self._save_memories()

        return True

    def process(self, message):
        """Process a message to store or retrieve memories

        Args:
            message: Input message

        Returns:
            Response message
        """
        try:
            command = message.get("command", "").lower()
            content = message.get("content", "")
            metadata = message.get("metadata", {})
            entry_id = message.get("entry_id")

            if command == "add":
                # Add a new memory
                entry_id = self.add_memory(content, metadata)
                return {"status": "success", "action": "add", "entry_id": entry_id}

            elif command == "get" and entry_id:
                # Retrieve a specific memory
                entry = self.get_memory(entry_id)
                if not entry:
                    return {
                        "status": "error",
                        "message": f"Memory with ID {entry_id} not found",
                    }

                return {
                    "status": "success",
                    "action": "get",
                    "entry_id": entry_id,
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "access_count": entry.access_count,
                }

            elif command == "search":
                # Search for similar memories
                limit = message.get("limit", 5)
                results = self.search_memories(content, limit)

                return {
                    "status": "success",
                    "action": "search",
                    "query": content,
                    "results": [
                        {
                            "entry_id": entry.entry_id,
                            "content": entry.content,
                            "metadata": entry.metadata,
                            "similarity": similarity,
                            "access_count": entry.access_count,
                        }
                        for entry, similarity in results
                    ],
                }

            elif command == "update" and entry_id:
                # Update a memory
                success = self.update_memory(entry_id, content, metadata)

                if not success:
                    return {
                        "status": "error",
                        "message": f"Memory with ID {entry_id} not found",
                    }

                return {"status": "success", "action": "update", "entry_id": entry_id}

            elif command == "delete" and entry_id:
                # Delete a memory
                success = self.delete_memory(entry_id)

                return {
                    "status": "success" if success else "error",
                    "action": "delete",
                    "entry_id": entry_id,
                    "message": "Memory deleted" if success else "Memory not found",
                }

            elif command == "clear":
                # Clear all memories
                count = self.clear_memories()

                return {
                    "status": "success",
                    "action": "clear",
                    "count": count,
                    "message": f"Cleared {count} memories",
                }

            else:
                return {"status": "error", "message": f"Unknown command: {command}"}

        except VectorMemoryException as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return {"status": "error", "message": f"Internal error: {str(e)}"}
