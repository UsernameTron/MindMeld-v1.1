import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from ..api.client import ClaudeAPIClient
from .base import Memory

logger = logging.getLogger(__name__)


class ConversationMemory(Memory):
    """
    Specialized memory for storing and managing conversation history.
    Optimized for maintaining context in ongoing conversations.
    """

    def __init__(
        self,
        api_client: ClaudeAPIClient,
        name: str = "conversation_memory",
        max_turns: int = 20,
        max_tokens: int = 8000,
        ttl: Optional[int] = None,  # Time to live in seconds
    ):
        """
        Initialize the conversation memory.

        Args:
            api_client: Claude API client instance
            name: Name identifier for this memory
            max_turns: Maximum number of conversation turns to store
            max_tokens: Maximum number of tokens to store (approximate)
            ttl: Optional time-to-live in seconds for messages
        """
        super().__init__(name=name)
        self.api_client = api_client
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.ttl = ttl

        # Initialize conversation storage
        self.messages = []  # List of (message, role, timestamp, metadata)
        self.turn_ids = {}  # Map of turn_id to index in messages
        self.summary = ""  # Summary of older conversation history
        self.estimated_token_count = 0

    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a message to the conversation.

        Args:
            item: Message content (string or message object)
            metadata: Optional metadata with role, etc.

        Returns:
            ID of the stored message
        """
        # Process the message
        if isinstance(item, dict) and "content" in item:
            # If it's a message object
            content = item["content"]
            role = item.get(
                "role", metadata.get("role", "user") if metadata else "user"
            )
        else:
            # If it's just content
            content = str(item)
            role = metadata.get("role", "user") if metadata else "user"

        # Generate turn ID
        turn_id = (
            metadata.get("id", str(uuid.uuid4())) if metadata else str(uuid.uuid4())
        )

        # Store message with timestamp
        timestamp = time.time()
        message_data = {
            "content": content,
            "role": role,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        # Add to messages list
        self.messages.append(message_data)
        self.turn_ids[turn_id] = len(self.messages) - 1

        # Update token count estimate
        self.estimated_token_count += self._estimate_tokens(content)

        # Enforce limits
        self._enforce_limits()

        return turn_id

    def get(self, item_id: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        """
        Retrieve a specific message by ID.

        Args:
            item_id: ID of the message to retrieve

        Returns:
            Tuple of (message_content, metadata)
        """
        if item_id in self.turn_ids:
            idx = self.turn_ids[item_id]
            if idx < len(self.messages):
                message = self.messages[idx]

                # Check if expired
                if self.ttl is not None:
                    age = time.time() - message["timestamp"]
                    if age > self.ttl:
                        logger.debug(f"Message {item_id} has expired")
                        # Mark as expired but don't remove yet
                        return None, None

                return message["content"], message["metadata"]

        return None, None

    def search(
        self, query: Any, limit: int = 5
    ) -> List[Tuple[str, Any, Optional[Dict[str, Any]], float]]:
        """
        Search for relevant messages in the conversation history.

        Args:
            query: Search query (text to look for)
            limit: Maximum number of results to return

        Returns:
            List of tuples (message_id, content, metadata, relevance_score)
        """
        # Simple text search implementation
        query_str = str(query).lower()
        results = []

        # Check each message for the query string
        for turn_id, idx in self.turn_ids.items():
            if idx >= len(self.messages):
                continue

            message = self.messages[idx]
            content = message["content"]

            # Check if expired
            if self.ttl is not None:
                age = time.time() - message["timestamp"]
                if age > self.ttl:
                    continue

            # Simple relevance matching
            content_lower = content.lower()
            if query_str in content_lower:
                # Calculate simple relevance score based on:
                # 1. How recent the message is (newer = higher score)
                # 2. How many times the query appears
                # 3. Whether it's an exact match

                recency_factor = idx / max(
                    1, len(self.messages) - 1
                )  # 0 = oldest, 1 = newest
                occurrences = content_lower.count(query_str)
                exact_match = 1.2 if content_lower == query_str else 1.0

                relevance_score = (
                    (0.5 + 0.5 * recency_factor) * occurrences * exact_match
                )

                results.append(
                    (
                        turn_id,
                        content,
                        {"role": message["role"], "timestamp": message["timestamp"]},
                        relevance_score,
                    )
                )

        # Sort by relevance and limit results
        results.sort(key=lambda x: x[3], reverse=True)
        return results[:limit]

    def update(
        self, item_id: str, item: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing message.

        Args:
            item_id: ID of the message to update
            item: Updated message content
            metadata: Updated metadata

        Returns:
            True if successful, False otherwise
        """
        if item_id not in self.turn_ids:
            return False

        idx = self.turn_ids[item_id]
        if idx >= len(self.messages):
            return False

        # Get existing message
        message = self.messages[idx]

        # Calculate token difference for estimation
        old_tokens = self._estimate_tokens(message["content"])
        new_tokens = self._estimate_tokens(item)
        token_diff = new_tokens - old_tokens

        # Update content
        message["content"] = item

        # Update metadata if provided
        if metadata:
            if "role" in metadata:
                message["role"] = metadata["role"]

            # Update or merge other metadata
            if "metadata" in message:
                message["metadata"].update(metadata)
            else:
                message["metadata"] = metadata

        # Update token count estimate
        self.estimated_token_count += token_diff

        # Update timestamp
        message["timestamp"] = time.time()

        return True

    def remove(self, item_id: str) -> bool:
        """
        Remove a message from the conversation.

        Args:
            item_id: ID of the message to remove

        Returns:
            True if successful, False otherwise
        """
        if item_id not in self.turn_ids:
            return False

        idx = self.turn_ids[item_id]
        if idx >= len(self.messages):
            return False

        # Get message for token counting
        message = self.messages[idx]
        tokens = self._estimate_tokens(message["content"])

        # Remove the message (replace with None to maintain indices)
        self.messages[idx] = None

        # Update token count
        self.estimated_token_count -= tokens

        # Remove from ID mapping
        del self.turn_ids[item_id]

        return True

    def clear(self) -> None:
        """Clear all messages from the conversation."""
        self.messages = []
        self.turn_ids = {}
        self.summary = ""
        self.estimated_token_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the conversation memory.

        Returns:
            Dictionary of statistics
        """
        # Count valid (non-None) messages
        valid_messages = [m for m in self.messages if m is not None]

        # Count by role
        role_counts = {}
        for message in valid_messages:
            role = message["role"]
            role_counts[role] = role_counts.get(role, 0) + 1

        # Calculate time stats
        timestamps = [message["timestamp"] for message in valid_messages]
        current_time = time.time()

        return {
            "name": self.name,
            "type": "conversation",
            "message_count": len(valid_messages),
            "estimated_token_count": self.estimated_token_count,
            "max_tokens": self.max_tokens,
            "max_turns": self.max_turns,
            "ttl": self.ttl,
            "role_counts": role_counts,
            "has_summary": bool(self.summary),
            "oldest_message_age": current_time - min(timestamps) if timestamps else 0,
            "newest_message_age": current_time - max(timestamps) if timestamps else 0,
            "average_message_age": (
                current_time - (sum(timestamps) / len(timestamps)) if timestamps else 0
            ),
        }

    def get_formatted_history(
        self, include_summary: bool = True, max_turns: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get formatted conversation history suitable for sending to Claude API.

        Args:
            include_summary: Whether to include the summary of older messages
            max_turns: Maximum number of turns to include (None = all)

        Returns:
            List of message objects in Claude API format
        """
        # Filter out None values and expired messages
        valid_messages = []
        for message in self.messages:
            if message is None:
                continue

            # Check if expired
            if self.ttl is not None:
                age = time.time() - message["timestamp"]
                if age > self.ttl:
                    continue

            valid_messages.append(message)

        # Limit the number of turns if requested
        if max_turns is not None:
            valid_messages = valid_messages[-max_turns:]

        # Format messages for Claude API
        formatted_messages = []

        # Add summary as a system message if requested and available
        if include_summary and self.summary:
            formatted_messages.append(
                {
                    "role": "system",
                    "content": f"Previous conversation summary: {self.summary}",
                }
            )

        # Add messages
        for message in valid_messages:
            formatted_messages.append(
                {"role": message["role"], "content": message["content"]}
            )

        return formatted_messages

    def generate_summary(self) -> str:
        """
        Generate a summary of older conversation history using Claude.
        Useful when pruning the conversation to stay within token limits.

        Returns:
            Generated summary
        """
        # Get messages to summarize (older messages beyond max_turns)
        older_messages = (
            self.messages[: -self.max_turns]
            if len(self.messages) > self.max_turns
            else []
        )

        # Filter out None values and expired messages
        valid_older_messages = []
        for message in older_messages:
            if message is None:
                continue

            # Check if expired
            if self.ttl is not None:
                age = time.time() - message["timestamp"]
                if age > self.ttl:
                    continue

            valid_older_messages.append(message)

        # If no older messages, return empty summary
        if not valid_older_messages:
            return ""

        try:
            # Format messages for Claude
            formatted_messages = []
            for message in valid_older_messages:
                formatted_messages.append(
                    {"role": message["role"], "content": message["content"]}
                )

            # Add the summarization request
            formatted_messages.append(
                {
                    "role": "user",
                    "content": "Please summarize our conversation so far, including key points and any decisions made. Keep the summary concise but comprehensive.",
                }
            )

            # Get summary from Claude
            response = self.api_client.send_message(
                messages=formatted_messages, max_tokens=500, temperature=0.3
            )

            # Extract summary
            summary = response.content[0].text if response.content else ""
            self.summary = summary

            return summary

        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            return "Error generating summary"

    def _enforce_limits(self) -> None:
        """
        Enforce turn and token limits by removing older messages or generating summaries.
        """
        # First check for any messages to prune
        self._remove_expired()

        # Check if we're over the token limit
        if self.estimated_token_count > self.max_tokens:
            logger.info(
                f"Conversation over token limit ({self.estimated_token_count} > {self.max_tokens})"
            )

            # Generate summary of older messages if needed
            if len(self.messages) > self.max_turns:
                self.generate_summary()

            # Remove older messages to get under token limit
            while (
                self.estimated_token_count > self.max_tokens and len(self.messages) > 0
            ):
                if self.messages[0] is not None:
                    tokens = self._estimate_tokens(self.messages[0]["content"])
                    self.estimated_token_count -= tokens

                # Remove the oldest message
                self.messages.pop(0)

                # Update turn_ids to reflect new indices
                self.turn_ids = {
                    turn_id: idx - 1
                    for turn_id, idx in self.turn_ids.items()
                    if idx > 0  # Keep only messages that are still in the list
                }

        # Check if we're over the turn limit
        if len(self.messages) > self.max_turns:
            logger.info(
                f"Conversation over turn limit ({len(self.messages)} > {self.max_turns})"
            )

            # Generate summary of older messages
            self.generate_summary()

            # Find how many messages to remove
            excess = len(self.messages) - self.max_turns

            # Update token count for messages to be removed
            for i in range(excess):
                if self.messages[i] is not None:
                    tokens = self._estimate_tokens(self.messages[i]["content"])
                    self.estimated_token_count -= tokens

            # Remove oldest messages
            self.messages = self.messages[excess:]

            # Update turn_ids to reflect new indices
            self.turn_ids = {
                turn_id: idx - excess
                for turn_id, idx in self.turn_ids.items()
                if idx >= excess  # Keep only messages that are still in the list
            }

    def _remove_expired(self) -> None:
        """Remove messages that have expired due to TTL."""
        if self.ttl is None:
            return

        current_time = time.time()
        expired_indices = []

        for i, message in enumerate(self.messages):
            if message is None:
                continue

            age = current_time - message["timestamp"]
            if age > self.ttl:
                expired_indices.append(i)

                # Update token count
                tokens = self._estimate_tokens(message["content"])
                self.estimated_token_count -= tokens

                # Mark as expired (None)
                self.messages[i] = None

        # Remove from turn_ids mapping
        for turn_id, idx in list(self.turn_ids.items()):
            if idx in expired_indices:
                del self.turn_ids[turn_id]

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
