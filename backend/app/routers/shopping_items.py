from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.product import Product
from app.models.shopping_item import ShoppingItem
from app.models.user import User
from app.schemas.shopping_item import (
    ShoppingItemCreate,
    ShoppingItemResponse,
    ShoppingItemUpdate,
)
from app.models.shopping_history import ShoppingHistory


router = APIRouter(
    prefix="/items",
    tags=["Shopping List"],
)


@router.patch(
    "/complete-all",
    response_model=list[ShoppingItemResponse],
)
def complete_all_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all active shopping items as completed."""
    active_items = db.scalars(
        select(ShoppingItem).where(
            ShoppingItem.user_id == current_user.id,
            ShoppingItem.completed.is_(False),
        )
    ).all()

    for item in active_items:
        item.completed = True
        history = ShoppingHistory(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit=item.unit,
        )
        db.add(history)

    db.commit()
    for item in active_items:
        db.refresh(item)

    return list(active_items)


@router.post(
    "",
    response_model=ShoppingItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    item_data: ShoppingItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.scalar(
        select(Product).where(
            Product.id == item_data.product_id,
            Product.available.is_(True),
        )
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    existing_item = db.scalar(
        select(ShoppingItem).where(
            ShoppingItem.user_id == current_user.id,
            ShoppingItem.product_id == item_data.product_id,
        )
    )

    if existing_item:
        if existing_item.completed:
            # Re-adding a completed item resets it as a fresh entry.
            existing_item.quantity = item_data.quantity
            existing_item.completed = False
        else:
            existing_item.quantity += item_data.quantity

        if item_data.unit is not None:
            existing_item.unit = item_data.unit

        db.commit()
        db.refresh(existing_item)

        return existing_item

    item = ShoppingItem(
        user_id=current_user.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        unit=item_data.unit,
        completed=False,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get(
    "",
    response_model=list[ShoppingItemResponse],
)
def get_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.scalars(
        select(ShoppingItem)
        .where(ShoppingItem.user_id == current_user.id)
        .order_by(ShoppingItem.created_at.desc())
    ).all()

    return items


@router.get(
    "/{item_id}",
    response_model=ShoppingItemResponse,
)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == current_user.id,
        )
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping item not found",
        )

    return item


@router.patch(
    "/{item_id}",
    response_model=ShoppingItemResponse,
)
def update_item(
    item_id: int,
    item_data: ShoppingItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == current_user.id,
        )
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping item not found",
        )

    was_completed = item.completed

    if "quantity" in item_data.model_fields_set:
        if item_data.quantity is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Quantity cannot be null",
            )

        item.quantity = item_data.quantity

    if "unit" in item_data.model_fields_set:
        item.unit = item_data.unit

    if "completed" in item_data.model_fields_set:
        if item_data.completed is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Completed cannot be null",
            )

        item.completed = item_data.completed

    # Record a purchase only when the item transitions
    # from incomplete to completed.
    became_completed = not was_completed and item.completed

    if became_completed:
        history = ShoppingHistory(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit=item.unit,
        )

        db.add(history)

    # Shopping item update and history insertion
    # are committed together.
    db.commit()
    db.refresh(item)

    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(ShoppingItem).where(
            ShoppingItem.id == item_id,
            ShoppingItem.user_id == current_user.id,
        )
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping item not found",
        )

    db.delete(item)
    db.commit()
