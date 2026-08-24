import logging
import os

import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)


class _NullRedis:
    """A no-op Redis stub used when the real Redis server is unavailable.
    All operations silently succeed or return None so the app keeps running."""

    def get(self, *a, **kw):
        return None

    def set(self, *a, **kw):
        return None

    def setex(self, *a, **kw):
        return None

    def incr(self, *a, **kw):
        return 0

    def expire(self, *a, **kw):
        return None

    def delete(self, *a, **kw):
        return None

    def __getattr__(self, name):
        # Catch-all for any other Redis command
        def _noop(*a, **kw):
            return None
        return _noop


def _make_client():
    try:
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        return client
    except Exception:
        logger.warning("Redis unavailable — using no-op stub. Caching and rate-limiting are disabled.")
        return _NullRedis()


redis_client = _make_client()


def get_redis():
    return redis_client
