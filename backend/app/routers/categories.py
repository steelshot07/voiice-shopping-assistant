from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.get(
    "",
    response_model=list[CategoryResponse],
)
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = db.scalars(
        select(Category).order_by(Category.name.asc())
    ).all()

    return categories
