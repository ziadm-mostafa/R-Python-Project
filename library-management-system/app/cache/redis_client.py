import os
import redis
import logging


logger = logging.getLogger("library.redis")

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=0,
    decode_responses=True
)


def check_redis() -> bool:
    try:
        redis_client.ping()
        return True
    except redis.RedisError as e:
        logger.warning(f"redis connection failed: {e}")
        return False