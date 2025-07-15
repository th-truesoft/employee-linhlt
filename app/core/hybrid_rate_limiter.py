"""
Hybrid rate limiter with Redis support and in-memory fallback.
"""

import time
import logging
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status

from app.core.config import settings
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class HybridRateLimiter:
    """
    Enterprise-grade rate limiter with Redis support and in-memory fallback.

    Features:
    - Redis-based distributed rate limiting for production
    - Automatic fallback to in-memory for development/offline scenarios
    - Multi-tenant support with organization isolation
    - Token bucket algorithm for smooth rate limiting
    - Graceful degradation when Redis is unavailable
    """

    def __init__(self, rate_limit: int = 100, window_size: int = 60):
        """
        Initialize the hybrid rate limiter.

        Args:
            rate_limit: Maximum number of requests allowed in the window
            window_size: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.window_size = window_size

        # In-memory fallback storage
        self.memory_tokens: Dict[str, Tuple[int, float]] = {}

        # Redis connection status
        self._redis_available = False

    def _get_client_id(self, request: Request) -> str:
        """
        Get a unique identifier for the client with organization isolation.

        Format: {client_ip}:{organization_id}:{user_id}
        This ensures each organization has separate rate limit quotas.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Include organization_id from request state (set by middleware)
        organization_id = getattr(request.state, "organization_id", "default")

        # Include user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"rate_limit:{client_ip}:{organization_id}:{user_id}"

        return f"rate_limit:{client_ip}:{organization_id}"

    async def _init_redis_if_needed(self) -> None:
        """Initialize Redis connection if not already done."""
        if not self._redis_available and settings.REDIS_RATE_LIMITING:
            self._redis_available = await redis_client.connect()

    async def _check_redis_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check rate limit using Redis sliding window.

        Returns:
            Tuple[bool, int]: (is_allowed, retry_after_seconds)
        """
        try:
            current_time = int(time.time())
            window_start = current_time - self.window_size

            # Use Redis sliding window approach
            key = f"{client_id}:window"

            # Remove old entries and count current requests
            # This is an atomic operation in Redis
            pipe = redis_client._redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.expire(key, self.window_size)
            results = await pipe.execute()

            current_requests = results[1]

            if current_requests >= self.rate_limit:
                retry_after = int(self.window_size / self.rate_limit)
                return False, retry_after

            # Add current request to window
            await redis_client._redis.zadd(key, {str(current_time): current_time})
            await redis_client._redis.expire(key, self.window_size)

            return True, 0

        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}")
            # Fall back to in-memory if Redis fails
            self._redis_available = False
            return await self._check_memory_rate_limit(client_id)

    async def _check_memory_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check rate limit using in-memory token bucket.

        Returns:
            Tuple[bool, int]: (is_allowed, retry_after_seconds)
        """
        self._refill_tokens(client_id)

        if client_id not in self.memory_tokens:
            self.memory_tokens[client_id] = (self.rate_limit - 1, time.time())
            return True, 0

        tokens, _ = self.memory_tokens[client_id]

        if tokens <= 0:
            retry_after = int(self.window_size / self.rate_limit)
            return False, retry_after

        # Consume one token
        self.memory_tokens[client_id] = (tokens - 1, self.memory_tokens[client_id][1])
        return True, 0

    def _refill_tokens(self, client_id: str) -> None:
        """Refill tokens based on time elapsed since last refill."""
        if client_id not in self.memory_tokens:
            self.memory_tokens[client_id] = (self.rate_limit, time.time())
            return

        tokens, last_refill_time = self.memory_tokens[client_id]
        now = time.time()
        time_passed = now - last_refill_time

        # Calculate how many tokens to add based on time passed
        new_tokens = int(time_passed * (self.rate_limit / self.window_size))

        if new_tokens > 0:
            tokens = min(tokens + new_tokens, self.rate_limit)
            self.memory_tokens[client_id] = (tokens, now)

    async def check_rate_limit(self, request: Request) -> None:
        """
        Check if the request exceeds the rate limit.
        Uses Redis if available, falls back to in-memory.

        Raises:
            HTTPException: If the rate limit is exceeded
        """
        client_id = self._get_client_id(request)

        # Try to initialize Redis if needed
        await self._init_redis_if_needed()

        # Choose rate limiting strategy
        if self._redis_available:
            logger.debug(f"Using Redis rate limiting for {client_id}")
            is_allowed, retry_after = await self._check_redis_rate_limit(client_id)
        else:
            logger.debug(f"Using in-memory rate limiting for {client_id}")
            is_allowed, retry_after = await self._check_memory_rate_limit(client_id)

        if not is_allowed:
            headers = {"Retry-After": str(retry_after)}

            # Add rate limiting info to headers
            headers["X-RateLimit-Limit"] = str(self.rate_limit)
            headers["X-RateLimit-Window"] = str(self.window_size)
            headers["X-RateLimit-Backend"] = (
                "redis" if self._redis_available else "memory"
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "rate_limit": self.rate_limit,
                    "window_size": self.window_size,
                    "backend": "redis" if self._redis_available else "memory",
                },
                headers=headers,
            )

    async def get_rate_limit_info(self, request: Request) -> Dict[str, any]:
        """
        Get current rate limit information for debugging.

        Returns:
            Dict with current rate limit status
        """
        client_id = self._get_client_id(request)

        info = {
            "client_id": client_id,
            "rate_limit": self.rate_limit,
            "window_size": self.window_size,
            "backend": "redis" if self._redis_available else "memory",
            "redis_available": self._redis_available,
        }

        if self._redis_available:
            try:
                current_time = int(time.time())
                window_start = current_time - self.window_size
                key = f"{client_id}:window"

                # Get current request count
                current_requests = await redis_client._redis.zcard(key)
                remaining = max(0, self.rate_limit - current_requests)

                info.update(
                    {
                        "current_requests": current_requests,
                        "remaining_requests": remaining,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to get Redis rate limit info: {e}")
                info["error"] = str(e)
        else:
            # Get in-memory info
            if client_id in self.memory_tokens:
                tokens, last_refill = self.memory_tokens[client_id]
                info.update({"current_tokens": tokens, "last_refill": last_refill})

        return info


# Create global hybrid rate limiter instance
hybrid_rate_limiter = HybridRateLimiter(
    rate_limit=getattr(settings, "RATE_LIMIT", 100),
    window_size=getattr(settings, "RATE_LIMIT_WINDOW_SIZE", 60),
)
