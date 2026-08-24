import logging

from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    # Do not trust X-Forwarded-For unless your deployment is behind
    # a trusted proxy that overwrites it.
    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request: Request,
    key_prefix: str,
    identifier: str | None = None,
) -> None:
    try:
        redis = get_redis()

        if identifier:
            key = f"rate:{key_prefix}:user:{identifier}"
        else:
            ip = get_client_ip(request)
            key = f"rate:{key_prefix}:ip:{ip}"

        current = redis.incr(key)

        if current == 1:
            redis.expire(
                key,
                settings.rate_limit_window_seconds,
            )

        if current > settings.rate_limit_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )
    except HTTPException:
        # Re-raise rate limit errors
        raise
    except Exception:
        # Redis unavailable — fail open and allow the request
        logger.warning("Rate limiter unavailable (Redis not connected). Skipping rate limit check.")
