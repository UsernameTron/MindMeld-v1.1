import logging
import os
import time
from typing import Any, Dict, List, Optional

import anthropic
from anthropic import Anthropic
from anthropic.types import Message, MessageParam

from ..utils.token_counter import TokenCounter
from ..utils.token_optimizer import TokenOptimizer

logger = logging.getLogger(__name__)


class OptimizedClaudeClient:
    """
    Optimized client for Claude API with built-in token optimization,
    caching, and cost controls.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        max_retries: int = 5,
        backoff_factor: float = 1.5,
        max_tokens: int = 4096,
        budget_tier: str = "standard",
        enable_caching: bool = True,
        cache_ttl: int = 3600,  # Cache time-to-live in seconds
        cost_tracking: bool = True,
    ):
        """
        Initialize the optimized Claude API client.

        Args:
            api_key: Claude API key (defaults to ANTHROPIC_API_KEY environment variable)
            model: Claude model to use
            max_retries: Maximum number of retries for failed API calls
            backoff_factor: Exponential backoff factor for retries
            max_tokens: Maximum number of tokens in the response
            budget_tier: Cost optimization tier (economy, standard, premium)
            enable_caching: Whether to enable response caching
            cache_ttl: Cache time-to-live in seconds
            cost_tracking: Whether to track API costs
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set as ANTHROPIC_API_KEY environment variable"
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_tokens = max_tokens
        self.budget_tier = budget_tier
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.cost_tracking = cost_tracking

        # Initialize token counter
        self.token_counter = TokenCounter(model_name=model)

        # Initialize response cache
        self.response_cache = {}

        # Initialize cost tracking
        self.cost_tracker = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "request_count": 0,
            "cache_hits": 0,
            "start_time": time.time(),
        }

    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff time in seconds."""
        return min(60, self.backoff_factor**attempt)

    def _generate_cache_key(self, params: Dict[str, Any]) -> str:
        """Generate a cache key from request parameters."""
        import hashlib
        import json

        # Create a simplified version of the params for hashing
        cache_params = {
            "model": params.get("model", ""),
            "messages": params.get("messages", []),
            "system": params.get("system", ""),
            "temperature": params.get("temperature", 0.7),
            "tools": "tools" in params,  # Just check if tools are present
            "max_tokens": params.get("max_tokens", 0),
        }

        # Convert to JSON string and hash
        param_str = json.dumps(cache_params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if a cached response is still valid based on TTL."""
        return (time.time() - timestamp) < self.cache_ttl

    def _track_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Track token usage and cost."""
        if not self.cost_tracking:
            return

        # Add to counts
        self.cost_tracker["prompt_tokens"] += prompt_tokens
        self.cost_tracker["completion_tokens"] += completion_tokens
        self.cost_tracker["total_tokens"] += prompt_tokens + completion_tokens
        self.cost_tracker["request_count"] += 1

        # Calculate cost based on the model
        cost = self.token_counter.estimate_cost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=self.model,
        )

        self.cost_tracker["total_cost"] += cost

    def _track_cache_hit(self) -> None:
        """Track cache hit."""
        if not self.cost_tracking:
            return

        self.cost_tracker["cache_hits"] += 1

    def send_message(
        self,
        messages: List[MessageParam],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        optimization_level: Optional[str] = None,  # Override budget_tier for this call
        bypass_cache: bool = False,
    ) -> Message:
        """
        Send a message to Claude with optimization and caching.

        Args:
            messages: List of message objects for the conversation
            system: System prompt for Claude
            max_tokens: Maximum number of tokens to generate (overrides default)
            temperature: Sampling temperature (0-1)
            tools: Optional list of tool definitions
            optimization_level: Optional override for budget_tier
            bypass_cache: Whether to bypass the cache for this request

        Returns:
            Claude API response
        """
        # Set up optimization level
        opt_level = optimization_level or self.budget_tier

        # Prepare API call parameters
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
        }

        if system:
            params["system"] = system

        if tools:
            params["tools"] = tools

        # Apply token optimization
        optimized_params = TokenOptimizer.optimize_api_parameters(
            params, budget_tier=opt_level
        )

        # Check cache before API call (if enabled and not bypassed)
        if (
            self.enable_caching and not bypass_cache and not tools
        ):  # Don't cache tool calls
            cache_key = self._generate_cache_key(optimized_params)

            if cache_key in self.response_cache:
                cached_response, timestamp = self.response_cache[cache_key]

                if self._is_cache_valid(timestamp):
                    logger.debug(f"Cache hit for request {cache_key[:8]}")
                    self._track_cache_hit()
                    return cached_response

        # Send request to API with retry logic
        attempts = 0

        while attempts < self.max_retries:
            try:
                # Track token usage before API call
                estimated_prompt_tokens = 0
                if optimized_params.get("messages"):
                    token_data = self.token_counter.count_message_tokens(
                        optimized_params["messages"]
                    )
                    estimated_prompt_tokens = token_data["prompt_tokens"]

                # Make the API call
                response = self.client.messages.create(**optimized_params)

                # Track usage after successful call
                completion_tokens = (
                    len(response.content[0].text) // 4
                )  # Simple approximation
                self._track_usage(estimated_prompt_tokens, completion_tokens)

                # Cache the response if caching is enabled and not a tool call
                if self.enable_caching and not tools:
                    cache_key = self._generate_cache_key(optimized_params)
                    self.response_cache[cache_key] = (response, time.time())

                    # Clean cache if it gets too large (>1000 entries)
                    if len(self.response_cache) > 1000:
                        # Remove oldest entries
                        oldest_keys = sorted(
                            self.response_cache.keys(),
                            key=lambda k: self.response_cache[k][1],
                        )[
                            :200
                        ]  # Remove oldest 200

                        for key in oldest_keys:
                            del self.response_cache[key]

                return response

            except anthropic.APIError as e:
                attempts += 1

                # Check if we should retry
                if attempts >= self.max_retries:
                    logger.error(f"Max retries exceeded. Last error: {str(e)}")
                    raise

                # Handle rate limiting specifically
                if e.status_code == 429:
                    backoff_time = self._exponential_backoff(attempts)
                    logger.warning(
                        f"Rate limited. Retrying in {backoff_time} seconds..."
                    )
                    time.sleep(backoff_time)
                    continue

                # Handle server errors (5xx)
                if e.status_code >= 500:
                    backoff_time = self._exponential_backoff(attempts)
                    logger.warning(
                        f"Server error {e.status_code}. Retrying in {backoff_time} seconds..."
                    )
                    time.sleep(backoff_time)
                    continue

                # For other errors, raise immediately
                logger.error(f"API error: {str(e)}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics and cost tracking information.

        Returns:
            Dictionary with usage stats and cost information
        """
        if not self.cost_tracking:
            return {"cost_tracking_disabled": True}

        # Calculate running time
        runtime_seconds = time.time() - self.cost_tracker["start_time"]
        runtime_days = runtime_seconds / (60 * 60 * 24)

        # Calculate average metrics
        avg_prompt_tokens = 0
        avg_completion_tokens = 0
        avg_cost_per_request = 0

        if self.cost_tracker["request_count"] > 0:
            avg_prompt_tokens = (
                self.cost_tracker["prompt_tokens"] / self.cost_tracker["request_count"]
            )
            avg_completion_tokens = (
                self.cost_tracker["completion_tokens"]
                / self.cost_tracker["request_count"]
            )
            avg_cost_per_request = (
                self.cost_tracker["total_cost"] / self.cost_tracker["request_count"]
            )

        # Calculate cache efficiency
        cache_hit_rate = 0
        if (self.cost_tracker["request_count"] + self.cost_tracker["cache_hits"]) > 0:
            cache_hit_rate = self.cost_tracker["cache_hits"] / (
                self.cost_tracker["request_count"] + self.cost_tracker["cache_hits"]
            )

        # Project monthly cost based on current usage
        projected_monthly_cost = 0
        if runtime_days > 0:
            daily_cost = self.cost_tracker["total_cost"] / runtime_days
            projected_monthly_cost = daily_cost * 30.44  # Average days in month

        # Create stats dictionary
        return {
            "model": self.model,
            "budget_tier": self.budget_tier,
            "runtime_seconds": runtime_seconds,
            "runtime_days": runtime_days,
            "request_count": self.cost_tracker["request_count"],
            "cache_hits": self.cost_tracker["cache_hits"],
            "cache_hit_rate": cache_hit_rate,
            "prompt_tokens": self.cost_tracker["prompt_tokens"],
            "completion_tokens": self.cost_tracker["completion_tokens"],
            "total_tokens": self.cost_tracker["total_tokens"],
            "avg_prompt_tokens": avg_prompt_tokens,
            "avg_completion_tokens": avg_completion_tokens,
            "total_cost": self.cost_tracker["total_cost"],
            "avg_cost_per_request": avg_cost_per_request,
            "projected_monthly_cost": projected_monthly_cost,
            "projected_annual_cost": projected_monthly_cost * 12,
        }

    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        self.cost_tracker = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "request_count": 0,
            "cache_hits": 0,
            "start_time": time.time(),
        }

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.response_cache = {}
        logger.info("Response cache cleared")

    def get_budget_projection(self, target_budget: float = 500.0) -> Dict[str, Any]:
        """
        Get budget projection and optimization recommendations.

        Args:
            target_budget: Target monthly budget in USD

        Returns:
            Budget projection with optimization recommendations
        """
        # Get current usage stats
        stats = self.get_usage_stats()

        # If we don't have enough data, make some assumptions
        if stats["request_count"] < 10:
            logger.warning(
                "Not enough data for accurate budget projection. Using default values."
            )
            # Default to medium usage assumptions
            avg_prompt_tokens = 1500
            avg_completion_tokens = 500
            requests_per_day = 100
        else:
            # Use actual data
            avg_prompt_tokens = stats["avg_prompt_tokens"]
            avg_completion_tokens = stats["avg_completion_tokens"]

            # Calculate requests per day
            if stats["runtime_days"] > 0:
                requests_per_day = stats["request_count"] / stats["runtime_days"]
            else:
                # Fallback if runtime is too short
                requests_per_day = 100

        # Get optimization recommendations
        return TokenOptimizer.optimize_for_budget(
            avg_prompt_tokens=avg_prompt_tokens,
            avg_completion_tokens=avg_completion_tokens,
            requests_per_day=requests_per_day,
            target_budget=target_budget,
            models=[
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        )
