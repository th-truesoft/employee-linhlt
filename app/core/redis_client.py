"""
Redis client with connection management and graceful fallback.
"""

import asyncio
import logging
from typing import Optional, Any
import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client with automatic connection management and graceful fallback.

    Features:
    - Automatic connection retry
    - Health checking
    - Graceful degradation when Redis is unavailable
    - Connection pooling
    """

    def __init__(self):
        self._redis: Optional[Redis] = None
        self._connected = False
        self._connection_lock = asyncio.Lock()

    async def connect(self) -> bool:
        """
        Connect to Redis with retry logic.

        Returns:
            bool: True if connected successfully, False otherwise
        """
        if not settings.REDIS_URL or not settings.REDIS_RATE_LIMITING:
            logger.info("Redis rate limiting disabled in configuration")
            return False

        async with self._connection_lock:
            if self._connected and self._redis:
                return True

            try:
                # Create Redis connection with optimized settings
                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                    socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                    retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                    health_check_interval=30,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                )

                # Test connection
                await self._redis.ping()
                self._connected = True
                logger.info("✅ Redis connected successfully")
                return True

            except (ConnectionError, TimeoutError, OSError) as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
                logger.info("📊 Falling back to in-memory rate limiting")
                self._connected = False
                self._redis = None
                return False

            except Exception as e:
                logger.error(f"❌ Unexpected Redis error: {e}")
                self._connected = False
                self._redis = None
                return False

    async def disconnect(self) -> None:
        """Close Redis connection."""
        async with self._connection_lock:
            if self._redis:
                try:
                    await self._redis.close()
                    logger.info("Redis connection closed")
                except Exception as e:
                    logger.warning(f"Error closing Redis connection: {e}")
                finally:
                    self._redis = None
                    self._connected = False

    async def is_connected(self) -> bool:
        """Check if Redis is connected and available."""
        if not self._connected or not self._redis:
            return False

        try:
            await self._redis.ping()
            return True
        except Exception:
            self._connected = False
            return False

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis with error handling.

        Returns:
            Optional[str]: Value if successful, None if Redis unavailable
        """
        if not await self.is_connected():
            return None

        try:
            return await self._redis.get(key)
        except RedisError as e:
            logger.warning(f"Redis GET error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set value in Redis with error handling.

        Returns:
            bool: True if successful, False if Redis unavailable
        """
        if not await self.is_connected():
            return False

        try:
            await self._redis.set(key, value, ex=ex)
            return True
        except RedisError as e:
            logger.warning(f"Redis SET error for key {key}: {e}")
            return False

    async def incr(self, key: str) -> Optional[int]:
        """
        Increment value in Redis with error handling.

        Returns:
            Optional[int]: New value if successful, None if Redis unavailable
        """
        if not await self.is_connected():
            return None

        try:
            return await self._redis.incr(key)
        except RedisError as e:
            logger.warning(f"Redis INCR error for key {key}: {e}")
            return None

    async def expire(self, key: str, time: int) -> bool:
        """
        Set expiration for key in Redis.

        Returns:
            bool: True if successful, False if Redis unavailable
        """
        if not await self.is_connected():
            return False

        try:
            await self._redis.expire(key, time)
            return True
        except RedisError as e:
            logger.warning(f"Redis EXPIRE error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.

        Returns:
            bool: True if successful, False if Redis unavailable
        """
        if not await self.is_connected():
            return False

        try:
            await self._redis.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Redis DELETE error for key {key}: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()
