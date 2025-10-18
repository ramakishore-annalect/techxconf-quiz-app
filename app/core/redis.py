"""Redis configuration and client management."""

import redis.asyncio as redis
from typing import Optional
from app.core.config import settings, get_redis_url

# Redis client instance
redis_client: Optional[redis.Redis] = None


async def init_redis() -> redis.Redis:
    """Initialize Redis connection."""
    global redis_client

    redis_client = redis.from_url(
        get_redis_url(),
        encoding="utf-8",
        decode_responses=True,
        health_check_interval=30,
        socket_keepalive=True,
        socket_keepalive_options={},
        retry_on_timeout=True,
        max_connections=20
    )

    # Test connection
    await redis_client.ping()
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client


# Cache utilities
class CacheManager:
    """Cache management utilities."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        return await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return bool(await self.redis.delete(key))

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.redis.exists(key))

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        return await self.redis.incrby(key, amount)

    async def set_with_ttl(self, key: str, value: str, ttl: int) -> bool:
        """Set key with TTL."""
        return await self.redis.setex(key, ttl, value)

    async def get_ttl(self, key: str) -> int:
        """Get TTL for key."""
        return await self.redis.ttl(key)


# Global cache manager instance
cache_manager: Optional[CacheManager] = None


async def get_cache() -> CacheManager:
    """Get cache manager."""
    global cache_manager
    if cache_manager is None:
        redis_client = await get_redis()
        cache_manager = CacheManager(redis_client)
    return cache_manager