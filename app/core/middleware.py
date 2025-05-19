"""Middleware module for the MindMeld application.

This module defines custom middleware for request ID management and rate limiting.

# Redis Fallback and IS_TESTING Behavior
#
# If Redis is unavailable, the system uses an in-memory MemoryRateLimiter for rate limiting.
# This fallback is especially useful for local development and CI environments.
#
# The IS_TESTING flag (see app/core/test_config.py) disables certain middleware and allows tests to bypass
# authentication and rate limiting logic for isolated testing.
"""

import time
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from app.core.config import get_redis
from app.core.logging import get_logger, set_request_id
from cachetools import TTLCache
from fastapi import HTTPException, Request, Response, status
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class MemoryRateLimiter:
    """
    In-memory rate limiter for environments without Redis.
    This version always removes the key after TTL.

    Attributes:
        counters (Dict[str, int]): Stores request counts per key.
        expiry (Dict[str, float]): Stores expiration times per key.
        lock (asyncio.Lock): Ensures thread safety for async operations.
    """
    def __init__(self) -> None:
        """
        Initialize the MemoryRateLimiter.
        """
        self.counters: Dict[str, int] = {}
        self.expiry: Dict[str, float] = {}
        import asyncio
        self.lock: asyncio.Lock = asyncio.Lock()

    async def incr(self, key: str) -> int:
        """
        Increment the request count for a key, resetting if expired.

        Args:
            key (str): The key to increment.

        Returns:
            int: The new request count for the key.
        """
        async with self.lock:
            now = time.time()
            if key in self.expiry and now > self.expiry[key]:
                print(f"[DEBUG] Expiring key '{key}' at {now}, expired at {self.expiry[key]}")
                self.counters.pop(key, None)
                self.expiry.pop(key, None)
            if key not in self.counters:
                self.counters[key] = 1
            else:
                self.counters[key] += 1
            print(f"[DEBUG] incr: key={key}, value={self.counters[key]}, expiry={self.expiry.get(key)}")
            return self.counters[key]

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set or clear the expiration for a key.

        Args:
            key (str): The key to expire.
            ttl (int): Time-to-live in seconds. If 0, expires immediately.

        Returns:
            bool: True if operation succeeded.
        """
        async with self.lock:
            if ttl == 0:
                print(f"[DEBUG] Forcing expire of key '{key}'")
                self.counters.pop(key, None)
                self.expiry.pop(key, None)
            else:
                self.expiry[key] = time.time() + ttl
            print(f"[DEBUG] expire: key={key}, ttl={ttl}, expiry={self.expiry.get(key)}")
            return True

    async def ttl(self, key: str) -> int:
        """
        Get the remaining TTL for a key.

        Args:
            key (str): The key to check.

        Returns:
            int: Seconds until expiration, or 0 if not set.
        """
        async with self.lock:
            if key in self.expiry:
                remaining = int(self.expiry[key] - time.time())
                print(f"[DEBUG] ttl: key={key}, remaining={remaining}")
                return max(0, remaining)
            print(f"[DEBUG] ttl: key={key}, no expiry")
            return 0

    async def reset_key(self, key: str) -> None:
        """
        Remove a key and its expiration from the limiter.

        Args:
            key (str): The key to remove.
        """
        async with self.lock:
            print(f"[DEBUG] reset_key: key={key}")
            self.counters.pop(key, None)
            self.expiry.pop(key, None)

# Example tier config (could be loaded from DB/config)
TIERS: Dict[str, Dict[str, int]] = {
    "basic": {"requests": 100, "window": 3600},
    "pro": {"requests": 1000, "window": 3600},
    "enterprise": {"requests": 10000, "window": 3600},
}


def get_tier_for_key(api_key: str) -> str:
    """
    Determine the tier for a given API key.

    Args:
        api_key: The API key to check.

    Returns:
        str: The tier name ('basic', 'pro', or 'enterprise').
    """
    if (api_key and api_key.startswith("pro_")):
        return "pro"
    if (api_key and api_key.startswith("ent_")):
        return "enterprise"
    return "basic"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID and log request information.

    Adds an X-Request-ID header to each response and logs request timing.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the middleware with the ASGI app."""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process the request and add a request ID to the response.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The processed response with X-Request-ID header.
        """
        request_id = request.headers.get("X-Request-ID")
        request_id = set_request_id(request_id)

        log = get_logger()

        start_time = time.time()
        log.info(f"Request started: {request.method} {request.url.path}")

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        process_time = time.time() - start_time
        log.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s"
        )

        return response


class RateLimiter:
    """
    Distributed rate limiter using Redis.
    Supports per-API-key and tiered quotas.

    Args:
        requests (int): Maximum requests allowed in the window.
        window (int): Time window in seconds.
        backend (optional): Injected backend for testing (MemoryRateLimiter or mock Redis).
    """

    def __init__(self, requests: int = 100, window: int = 3600, backend=None) -> None:
        """
        Initialize the rate limiter with default limits.

        Args:
            requests: Maximum number of requests allowed in the time window.
            window: Time window in seconds for the rate limit.
        """
        self.default_requests = requests
        self.default_window = window
        self.tracer = trace.get_tracer(__name__)
        self._backend = backend  # For test injection

    async def _get_backend(self):
        if self._backend is not None:
            return self._backend
        redis = await get_redis()
        if redis is None:
            redis = MemoryRateLimiter()
        return redis

    async def __call__(self, request: Request) -> None:
        """
        Apply rate limiting to the incoming request.

        Args:
            request: The incoming request to check against rate limits.

        Raises:
            HTTPException: If the rate limit is exceeded.
        """
        # Special handling for test mode
        if hasattr(request, "is_test_reset") and request.is_test_reset:
            return

        with self.tracer.start_as_current_span("rate_limit_check"):
            api_key = getattr(request.state, "api_key", None)
            # Use a fallback string for empty client host to avoid type issues
            client_host = (
                request.client.host
                if request.client and hasattr(request.client, "host")
                else "unknown"
            )
            identifier = api_key or client_host
            tier = get_tier_for_key(api_key) if api_key else None
            if tier and tier in TIERS:
                limit = TIERS[tier]["requests"]
                window = TIERS[tier]["window"]
            else:
                limit = self.default_requests
                window = self.default_window
            key = f"ratelimit:{identifier}:{request.url.path}"
            
            redis = await self._get_backend()

            # Safe check if key exists before incrementing
            try:
                key_exists = await redis.exists(key)
                if not key_exists:
                    print(f"[DEBUG] Key {key} doesn't exist, creating new counter")
                    current = await redis.incr(key)
                    await redis.expire(key, window)
                else:
                    current = await redis.incr(key)
                    if current == 1:
                        await redis.expire(key, window)
            except AttributeError:
                # Fallback for Redis clients without exists method
                current = await redis.incr(key)
                if current == 1:
                    await redis.expire(key, window)
                    
            ttl = await redis.ttl(key)
            request.state._rate_limit_limit = limit
            request.state._rate_limit_reset = int(time.time() + ttl if ttl > 0 else window)
            if current >= int(limit * 0.8) and current < limit:
                logger = get_logger()
                logger.warning(
                    f"Rate limit approaching: {identifier} at {current}/{limit} requests for {request.url.path}"
                )
                request.state._rate_limit_warning = True
                request.state._rate_limit_remaining = limit - current
            if current > limit:
                logger = get_logger()
                logger.warning(
                    f"Rate limit exceeded: {identifier}, Path: {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(ttl if ttl > 0 else window)},
                )


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to responses.

    Adds X-RateLimit-Limit, X-RateLimit-Reset, and warning headers if applicable.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process the request and add rate limit headers to the response.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The processed response with rate limit headers added.
        """
        response = await call_next(request)
        if hasattr(request.state, "_rate_limit_limit"):
            response.headers["X-RateLimit-Limit"] = str(request.state._rate_limit_limit)
        if hasattr(request.state, "_rate_limit_reset"):
            response.headers["X-RateLimit-Reset"] = str(request.state._rate_limit_reset)
        if (
            hasattr(request.state, "_rate_limit_warning")
            and request.state._rate_limit_warning
        ):
            response.headers["X-RateLimit-Warning"] = "true"
            response.headers["X-RateLimit-Remaining"] = str(
                request.state._rate_limit_remaining
            )
        return response


# Example usage in FastAPI endpoint:
# from app.core.middleware import RateLimiter
# @app.get("/some-endpoint", dependencies=[Depends(RateLimiter(requests=10, window=60))])
# def some_endpoint():
#     ...

# For future: Use aioredis or redis-py for distributed rate limiting.
