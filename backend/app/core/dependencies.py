from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rate_limit import check_rate_limit
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    try:
        user_id = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user


def rate_limit_by_ip(request: Request) -> None:
    check_rate_limit(
        request=request,
        key_prefix="general",
    )


def rate_limit_authenticated_user(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    check_rate_limit(
        request=request,
        key_prefix="user",
        identifier=str(current_user.id),
    )

    return current_user


def rate_limit_auth(request: Request) -> None:
    check_rate_limit(
        request=request,
        key_prefix="auth",
    )
