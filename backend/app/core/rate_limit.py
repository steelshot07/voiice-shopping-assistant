from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.redis import get_redis


def get_client_ip(request: Request) -> str:
    # Do not trust X-Forwarded-For unless your deployment is behind
    # a trusted proxy that overwrites it.
    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request: Request,
    key_prefix: str,
    identifier: str | None = None,
) -> None:
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
