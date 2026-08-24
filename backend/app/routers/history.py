from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.search_history import SearchHistory
from app.models.shopping_history import ShoppingHistory
from app.models.user import User
from app.schemas.history import (
    SearchHistoryResponse,
    ShoppingHistoryResponse,
)


router = APIRouter(
    prefix="/history",
    tags=["History"],
)


@router.get(
    "/search",
    response_model=list[SearchHistoryResponse],
)
def get_search_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = db.scalars(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.searched_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return history


@router.get(
    "/purchases",
    response_model=list[ShoppingHistoryResponse],
)
def get_purchase_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = db.scalars(
        select(ShoppingHistory)
        .where(ShoppingHistory.user_id == current_user.id)
        .order_by(ShoppingHistory.purchased_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return history
