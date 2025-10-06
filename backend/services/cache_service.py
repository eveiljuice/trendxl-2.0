"""
Caching service using Redis for TrendXL 2.0
"""
import json
import logging
from typing import Any, Optional, Dict
import redis
from config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data using Redis"""

    def __init__(self):
        """Initialize Redis connection"""
        # Disable Redis if REDIS_URL is not explicitly set
        if not settings.redis_url or settings.redis_url.strip() == "":
            logger.info("ℹ️ Redis caching disabled (REDIS_URL not configured)")
            self.redis_client = None
            self.enabled = False
            return

        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("✅ Redis cache service initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {e}")
            logger.info("💡 To enable Redis caching:")
            logger.info("   - Install Redis: https://redis.io/download")
            logger.info("   - Or run: docker run -d -p 6379:6379 redis:alpine")
            logger.info("   - Or use Redis Cloud: https://redis.com/try-free/")
            self.redis_client = None
            self.enabled = False

    def _get_key(self, key_type: str, identifier: str) -> str:
        """Generate cache key with namespace"""
        return f"trendxl:v2:{key_type}:{identifier}"

    async def get(self, key_type: str, identifier: str) -> Optional[Any]:
        """
        Get data from cache

        Args:
            key_type: Type of data (profile, posts, trends, etc.)
            identifier: Unique identifier for the data

        Returns:
            Cached data or None if not found
        """
        if not self.enabled:
            return None

        try:
            cache_key = self._get_key(key_type, identifier)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                logger.debug(f"Cache HIT for key: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"Cache MISS for key: {cache_key}")
                return None

        except Exception as e:
            logger.warning(f"Cache GET error for {key_type}:{identifier}: {e}")
            return None

    async def set(
        self,
        key_type: str,
        identifier: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store data in cache

        Args:
            key_type: Type of data (profile, posts, trends, etc.)
            identifier: Unique identifier for the data
            data: Data to cache
            ttl: Time to live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            cache_key = self._get_key(key_type, identifier)

            # Set default TTL based on key type
            if ttl is None:
                ttl_map = {
                    'profile': settings.cache_profile_ttl,
                    'posts': settings.cache_posts_ttl,
                    'trends': settings.cache_trends_ttl,
                    'hashtag': settings.cache_trends_ttl,
                    'users': settings.cache_posts_ttl
                }
                ttl = ttl_map.get(key_type, 300)  # Default 5 minutes

            # Serialize data to JSON
            serialized_data = json.dumps(data, default=str)

            # Store in Redis with TTL
            result = self.redis_client.setex(cache_key, ttl, serialized_data)

            if result:
                logger.debug(
                    f"Cache SET successful for key: {cache_key} (TTL: {ttl}s)")
                return True
            else:
                logger.warning(f"Cache SET failed for key: {cache_key}")
                return False

        except Exception as e:
            logger.warning(f"Cache SET error for {key_type}:{identifier}: {e}")
            return False

    async def delete(self, key_type: str, identifier: str) -> bool:
        """
        Delete data from cache

        Args:
            key_type: Type of data
            identifier: Unique identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            cache_key = self._get_key(key_type, identifier)
            result = self.redis_client.delete(cache_key)

            logger.debug(f"Cache DELETE for key: {cache_key}")
            return bool(result)

        except Exception as e:
            logger.warning(
                f"Cache DELETE error for {key_type}:{identifier}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Pattern to match (use * for wildcards)

        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0

        try:
            full_pattern = f"trendxl:v2:{pattern}"
            keys = self.redis_client.keys(full_pattern)

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(
                    f"Cleared {deleted} cache keys matching pattern: {full_pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.warning(f"Cache CLEAR error for pattern {pattern}: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {"enabled": False, "error": "Redis not available"}

        try:
            info = self.redis_client.info()

            # Get key count for our namespace
            keys = self.redis_client.keys("trendxl:v2:*")

            return {
                "enabled": True,
                "connected": True,
                "total_keys": len(keys),
                "used_memory": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                "enabled": True,
                "connected": False,
                "error": str(e)
            }

    async def health_check(self) -> bool:
        """
        Check if cache service is healthy

        Returns:
            True if healthy, False otherwise
        """
        if not self.enabled:
            return False

        try:
            return self.redis_client.ping()
        except Exception:
            return False

    async def acquire_lock(self, lock_name: str, timeout: int = 30, wait_timeout: int = 10) -> bool:
        """
        Acquire a distributed lock using Redis

        Args:
            lock_name: Name of the lock (e.g., 'analysis:username')
            timeout: Lock expiration in seconds (default 30s)
            wait_timeout: How long to wait to acquire lock (default 10s)

        Returns:
            True if lock acquired, False otherwise
        """
        if not self.enabled:
            return True  # Allow operation if Redis is not available

        try:
            lock_key = f"trendxl:v2:lock:{lock_name}"
            # SET NX EX: Set if Not eXists with EXpiration
            result = self.redis_client.set(lock_key, "1", nx=True, ex=timeout)

            if result:
                logger.debug(f"Lock acquired: {lock_name}")
                return True
            else:
                logger.warning(f"Lock already held: {lock_name}")
                return False

        except Exception as e:
            logger.warning(f"Failed to acquire lock {lock_name}: {e}")
            return True  # Allow operation if lock fails

    async def release_lock(self, lock_name: str) -> bool:
        """
        Release a distributed lock

        Args:
            lock_name: Name of the lock to release

        Returns:
            True if released, False otherwise
        """
        if not self.enabled:
            return True

        try:
            lock_key = f"trendxl:v2:lock:{lock_name}"
            result = self.redis_client.delete(lock_key)

            if result:
                logger.debug(f"Lock released: {lock_name}")
                return True
            else:
                logger.warning(f"Lock not found: {lock_name}")
                return False

        except Exception as e:
            logger.warning(f"Failed to release lock {lock_name}: {e}")
            return False


# Global cache service instance
cache_service = CacheService()
