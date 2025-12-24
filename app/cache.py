import json
import hashlib
import logging
from typing import Optional, Callable, Any
from functools import wraps
from .redis import get_redis

logger = logging.getLogger(__name__)

def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a unique cache key from prefix and parameters"""
    key_str = f"{prefix}:{json.dumps(kwargs, sort_keys=True)}"

    # Hash if key is too long (Redis key limit is 512MB, but shorter is better)
    if len(key_str) > 250:
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    return key_str    

def get_from_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        redis_client = get_redis()
        cached_value = redis_client.get(key)
        if cached_value:
            logger.info(f'Cache HIT for key: {key}')
            return json.loads(cached_value)
        else:
            logger.info(f"Cache MISS for key: {key}")
            return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

def set_to_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value to cache with TTL in seconds"""
    try:
        redis_client = get_redis()
        redis_client.setex(key, ttl, json.dumps(value))
        logger.info(f"Cached Key: {key} with TTL: {ttl}s")
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False

def invalidate_cache(pattern: str) -> int:
    """Invalidate cache keys matching a pattern"""
    try:
        redis_client = get_redis()
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Invalidated {deleted} cache keys missing: {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        return 0                    
