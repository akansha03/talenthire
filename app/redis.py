import redis
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create redis connection

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

def get_redis():
    """Dependency to get Redis client"""
    try:
        # Test connection
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error : {e}")
        raise    