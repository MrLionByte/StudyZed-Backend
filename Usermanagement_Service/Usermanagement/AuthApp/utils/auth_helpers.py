import redis
import logging
from django.utils import timezone
from zoneinfo import ZoneInfo
from rest_framework.response import Response

from django.conf import settings

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(
    host=str(settings.REDIS_HOST), port=settings.REDIS_PORT, db=0, decode_responses=True
)


def ensure_login_count_exists(email):
    """Ensure login count key exists with a default value of 0 if missing"""
    if not email:
        raise ValueError("Email cannot be empty")

    key = f"{email}_login_count"
    try:
        if not redis_client.exists(key):
            redis_client.setex(key, 1800, 0)

    except redis.exceptions.RedisError as e:
        raise RuntimeError(f"Failed to ensure login count exists: {e}")


def increment_login_count(email):
    """Increment the login count for a user"""
    if not email:
        raise ValueError("Email cannot be empty")

    key = f"{email}_login_count"
    try:
        return redis_client.incr(key)

    except redis.exceptions.RedisError as e:
        raise RuntimeError(f"Failed to increment login count: {e}")


def check_login_count(email):
    """Check if login count exceeds 5 attempts"""
    if not email:
        raise ValueError("Email cannot be empty")

    key = f"{email}_login_count"
    try:
        count = redis_client.get(key)
        return count is not None and int(count) > 5
    except redis.exceptions.RedisError as e:
        raise RuntimeError(f"Failed to check login count: {e}")


def reset_login_count(email):
    """Reset login count to 0 by deleting the key (successful login)"""
    if not email:
        raise ValueError("Email cannot be empty")

    key = f"{email}_login_count"
    try:
        redis_client.delete(key)
    except redis.exceptions.RedisError as e:
        raise RuntimeError(f"Failed to reset login count: {e}")
