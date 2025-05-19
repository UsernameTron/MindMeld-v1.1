import json
import logging
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.agents.core.base import Agent
from src.ai.client import BaseLLMClient, LLMClientFactory
from src.ai.embeddings import EmbeddingService, EmbeddingVector

# Try to import vector database libraries
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    # Log warning instead of raising an exception, allowing fallback to non-FAISS implementation
    logging.warning(
        "faiss is not installed. For better performance, install it with 'pip install faiss-cpu' or 'pip install faiss-gpu'."
    )
    FAISS_AVAILABLE = False


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


class OptimizedVectorMemoryAgent(Agent):
    """Agent for semantic memory storage and retrieval using vector embeddings
    with performance optimizations"""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None,
        llm_client: Optional[BaseLLMClient] = None,
        index_name: str = "default",
        similarity_threshold: float = 0.7,
        use_faiss: bool = True,
        batch_size: int = 10,
        max_workers: int = 4,
    ):
        """Initialize the vector memory agent

        Args:
            storage_path: Path to store vector database
            embedding_service: Service for generating embeddings
            llm_client: LLM client for text generation
            index_name: Name of the vector index
            similarity_threshold: Threshold for similarity search
            use_faiss: Whether to use FAISS for vector search (if available)
            batch_size: Batch size for operations
            max_workers: Maximum number of worker threads
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
        self.batch_size = batch_size
        self.max_workers = max_workers

        # In-memory storage as a fallback or supplement to vector DB
        self._memory_entries: Dict[str, MemoryEntry] = {}

        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Lock for thread safety
        self.lock = threading.RLock()

        # FAISS index for fast similarity search
        if not FAISS_AVAILABLE and use_faiss:
            self.logger.warning(
                "FAISS library not available - falling back to brute force search"
            )

        self.use_faiss = use_faiss and FAISS_AVAILABLE
        self.faiss_index = None
        self.faiss_id_map = {}  # Maps FAISS index positions to entry_ids

        # Initialize vector store
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize the vector storage backend"""
        try:
            # Ensure storage directory exists
            os.makedirs(self.storage_path, exist_ok=True)

            # Attempt to load existing memories
            self._load_memories()

            # Initialize FAISS if available
            if self.use_faiss:
                self._initialize_faiss()

            self.logger.info(
                f"Vector memory initialized at: {self.storage_path} (using FAISS: {self.use_faiss})"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize vector storage: {str(e)}")
            self.logger.warning("Falling back to in-memory storage")

    def _initialize_faiss(self):
        """Initialize FAISS index with existing embeddings"""
        if not FAISS_AVAILABLE:
            self.logger.warning(
                "FAISS library not available - falling back to brute force search"
            )
            self.use_faiss = False
            return

        if not self._memory_entries:
            return

        try:
            # Get dimension from the first embedding
            first_entry = next(iter(self._memory_entries.values()))
            dim = len(first_entry.embedding)

            # Create FAISS index
            self.faiss_index = faiss.IndexFlatL2(dim)

            # Add existing embeddings to the index
            embeddings = []
            ids = []

            for i, (entry_id, entry) in enumerate(self._memory_entries.items()):
                embeddings.append(np.array(entry.embedding).astype("float32"))
                ids.append(i)
                self.faiss_id_map[i] = entry_id

            if embeddings:
                self.faiss_index.add(np.vstack(embeddings))

            self.logger.info(f"FAISS index initialized with {len(embeddings)} entries")
        except Exception as e:
            self.logger.error(f"Failed to initialize FAISS: {str(e)}")
            self.use_faiss = False

    def _get_cache_path(self, text: str) -> str:
        """Get cache file path for text"""
        text_hash = self.embedding_service._get_cache_path(text)
        return text_hash

    def _load_memories(self):
        """Load memories from disk"""
        index_path = os.path.join(self.storage_path, f"{self.index_name}.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r") as f:
                    entries_data = json.load(f)

                with self.lock:
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
            with self.lock:
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

    def _add_to_faiss(self, entry_id, embedding):
        """Add embedding to FAISS index"""
        if not FAISS_AVAILABLE:
            return

        if not self.use_faiss or not self.faiss_index:
            return

        try:
            with self.lock:
                # Get next index position
                idx = len(self.faiss_id_map)
                self.faiss_id_map[idx] = entry_id

                # Add to FAISS
                self.faiss_index.add(np.array([embedding]).astype("float32"))
        except Exception as e:
            self.logger.error(f"Failed to add to FAISS: {str(e)}")

    def _batch_embed(self, texts: List[str]) -> List[EmbeddingVector]:
        """Generate embeddings for multiple texts in parallel"""
        futures = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            futures.append(
                self.executor.submit(self.embedding_service.batch_get_embeddings, batch)
            )

        results = []
        for future in futures:
            results.extend(future.result())

        return results

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
            with self.lock:
                self._memory_entries[entry.entry_id] = entry

                # Add to FAISS if enabled
                if self.use_faiss:
                    self._add_to_faiss(entry.entry_id, entry.embedding)

            # Save to disk (non-blocking)
            self.executor.submit(self._save_memories)

            return entry.entry_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {str(e)}")
            raise VectorMemoryException(f"Failed to add memory: {str(e)}") from e

    def batch_add_memories(self, items: List[Dict[str, Any]]) -> List[str]:
        """Add multiple memories in batch

        Args:
            items: List of items with "content" and optional "metadata"

        Returns:
            List of memory entry IDs
        """
        try:
            # Extract contents for batched embedding
            contents = [item["content"] for item in items]

            # Generate embeddings in parallel batches
            embedding_results = self._batch_embed(contents)

            # Create memory entries
            entry_ids = []

            for i, embedding_result in enumerate(embedding_results):
                entry = MemoryEntry(
                    content=items[i]["content"],
                    embedding=embedding_result.vector,
                    metadata=items[i].get("metadata", {}),
                )

                # Store entry
                with self.lock:
                    self._memory_entries[entry.entry_id] = entry

                    # Add to FAISS if enabled
                    if self.use_faiss:
                        self._add_to_faiss(entry.entry_id, entry.embedding)

                entry_ids.append(entry.entry_id)

            # Save to disk (non-blocking)
            self.executor.submit(self._save_memories)

            return entry_ids
        except Exception as e:
            self.logger.error(f"Failed to batch add memories: {str(e)}")
            raise VectorMemoryException(
                f"Failed to batch add memories: {str(e)}"
            ) from e

    def get_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID

        Args:
            entry_id: ID of the memory to retrieve

        Returns:
            Memory entry or None if not found
        """
        with self.lock:
            entry = self._memory_entries.get(entry_id)
            if entry:
                # Update access stats
                entry.last_accessed = time.time()
                entry.access_count += 1
                return entry
        return None

    def search_memories_faiss(
        self, query_vector: List[float], limit: int = 5
    ) -> List[Tuple[MemoryEntry, float]]:
        """Search for memories using FAISS

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results

        Returns:
            List of (entry, similarity) tuples
        """
        if not FAISS_AVAILABLE:
            self.logger.debug("FAISS library not available for search")
            return []

        if not self.use_faiss or not self.faiss_index:
            return []

        try:
            # Convert to numpy array
            query_np = np.array([query_vector]).astype("float32")

            # Search FAISS index
            distances, indices = self.faiss_index.search(
                query_np, min(limit, len(self.faiss_id_map))
            )

            # Convert results
            results = []
            with self.lock:
                for i in range(len(indices[0])):
                    idx = indices[0][i]
                    if idx < 0:  # FAISS can return -1 for not enough results
                        continue

                    entry_id = self.faiss_id_map.get(idx)
                    if entry_id and entry_id in self._memory_entries:
                        entry = self._memory_entries[entry_id]

                        # Calculate cosine similarity (FAISS uses Euclidean distance)
                        # We convert to cosine similarity for consistent
                        # results
                        similarity = self.embedding_service.compute_similarity(
                            query_vector, entry.embedding
                        )

                        if similarity >= self.similarity_threshold:
                            results.append((entry, similarity))

                            # Update access stats
                            entry.last_accessed = time.time()
                            entry.access_count += 1

            return results
        except Exception as e:
            self.logger.error(f"FAISS search failed: {str(e)}")
            return []

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

            # Try FAISS search first if enabled
            if self.use_faiss and self.faiss_index:
                results = self.search_memories_faiss(query_embedding.vector, limit)
                if results:
                    return results

            # Fall back to brute force search
            results = []
            with self.lock:
                for entry in self._memory_entries.values():
                    similarity = self.embedding_service.compute_similarity(
                        query_embedding.vector, entry.embedding
                    )

                    if similarity >= self.similarity_threshold:
                        results.append((entry, similarity))

            # Sort by similarity (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            # Update access stats for retrieved memories
            with self.lock:
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
        with self.lock:
            if entry_id in self._memory_entries:
                del self._memory_entries[entry_id]

                # Note: We don't remove from FAISS index as it doesn't support deletion
                # Instead, we'll rebuild the index when it's needed
                if self.use_faiss:
                    self.faiss_index = None
                    self.faiss_id_map.clear()
                    self._initialize_faiss()

                # Save changes
                self.executor.submit(self._save_memories)
                return True
        return False

    def clear_memories(self) -> int:
        """Clear all memories

        Returns:
            Number of memories cleared
        """
        with self.lock:
            count = len(self._memory_entries)
            self._memory_entries.clear()

            # Reset FAISS index
            if self.use_faiss:
                self.faiss_index = None
                self.faiss_id_map.clear()

        # Save changes
        self.executor.submit(self._save_memories)
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
        with self.lock:
            entry = self._memory_entries.get(entry_id)
            if not entry:
                return False

            # Update content and regenerate embedding if provided
            if content is not None and content != entry.content:
                embedding_result = self.embedding_service.get_embedding(content)
                entry.content = content
                entry.embedding = embedding_result.vector

                # Update FAISS index
                if self.use_faiss:
                    # Rebuild index as FAISS doesn't support updates
                    self.faiss_index = None
                    self.faiss_id_map.clear()
                    self._initialize_faiss()

            # Update metadata if provided
            if metadata is not None:
                entry.metadata = {**entry.metadata, **metadata}

            # Update timestamp
            entry.last_accessed = time.time()

        # Save changes
        self.executor.submit(self._save_memories)

        return True

    def process(self, message):  # noqa: C901
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

            elif command == "batch_add":
                # Add multiple memories in batch
                items = message.get("items", [])
                if not items:
                    return {
                        "status": "error",
                        "message": "No items provided for batch add",
                    }

                entry_ids = self.batch_add_memories(items)
                return {
                    "status": "success",
                    "action": "batch_add",
                    "entry_ids": entry_ids,
                    "count": len(entry_ids),
                }

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

            elif command == "execute":
                # Handle execution requests from another agent
                description = message.get("description", "")
                context = message.get("context", {})

                # Try to interpret the task
                if "store" in description.lower() or "save" in description.lower():
                    if "content" in context:
                        entry_id = self.add_memory(
                            content=context["content"],
                            metadata=context.get("metadata", {}),
                        )
                        return {
                            "status": "success",
                            "action": "add",
                            "entry_id": entry_id,
                            "message": f"Stored memory: {context['content'][:50]}...",
                        }
                elif "search" in description.lower() or "find" in description.lower():
                    if "query" in context:
                        results = self.search_memories(
                            query=context["query"], limit=context.get("limit", 5)
                        )
                        return {
                            "status": "success",
                            "action": "search",
                            "results": [
                                {
                                    "content": entry.content,
                                    "similarity": similarity,
                                    "metadata": entry.metadata,
                                }
                                for entry, similarity in results
                            ],
                        }

                return {
                    "status": "error",
                    "message": f"Could not process task: {description}",
                }

            else:
                return {"status": "error", "message": f"Unknown command: {command}"}

        except VectorMemoryException as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return {"status": "error", "message": f"Internal error: {str(e)}"}

    def _search_with_faiss(
        self, query_vector: List[float], limit: int = 5
    ) -> List[Tuple[MemoryEntry, float]]:
        """Search for memories using FAISS index

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results

        Returns:
            List of (entry, similarity) tuples
        """
        # Delegate to the existing search_memories_faiss method
        return self.search_memories_faiss(query_vector, limit)

    def _rebuild_faiss_index(self):
        """Rebuild the FAISS index from scratch

        This is useful when many entries have been added/removed and
        the index needs to be optimized.
        """
        if not FAISS_AVAILABLE:
            self.logger.warning("FAISS library not available - cannot rebuild index")
            self.use_faiss = False
            return

        if not self.use_faiss:
            return

        try:
            with self.lock:
                # Get dimension from the first embedding
                if not self._memory_entries:
                    self.logger.warning("No memories to build index from")
                    return

                first_entry = next(iter(self._memory_entries.values()))
                dim = len(first_entry.embedding)

                # Create new FAISS index
                self.faiss_index = faiss.IndexFlatL2(dim)
                self.faiss_id_map = {}

                # Add all embeddings to the index
                embeddings = []
                ids = []

                for i, (entry_id, entry) in enumerate(self._memory_entries.items()):
                    embeddings.append(np.array(entry.embedding).astype("float32"))
                    ids.append(i)
                    self.faiss_id_map[i] = entry_id

                if embeddings:
                    self.faiss_index.add(np.vstack(embeddings))

                self.logger.info(f"Rebuilt FAISS index with {len(embeddings)} entries")

        except Exception as e:
            self.logger.error(f"Failed to rebuild FAISS index: {str(e)}")
            self.use_faiss = False
            self.logger.warning("Falling back to in-memory search")
