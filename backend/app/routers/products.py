import json
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.redis import get_redis
from app.database import get_db
from app.models.product import Product
from app.models.search_history import SearchHistory
from app.models.user import User
from app.schemas.product import ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


CACHE_TTL = 300  # 5 minutes


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(
    q: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    category_id: int | None = None,
    brand_id: int | None = None,
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    # Validate price range before querying.
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Minimum price cannot exceed maximum price",
        )

    # Normalize user input before using it for search/cache.
    normalized_query = q.strip().lower() if q else ""

    # Build a deterministic cache key.
    cache_key = (
        f"products:"
        f"q={normalized_query}:"
        f"brand={brand_id}:"
        f"category={category_id}:"
        f"min={min_price}:"
        f"max={max_price}:"
        f"limit={limit}:"
        f"offset={offset}"
    )

    # -----------------------------
    # 1. Check Redis
    # -----------------------------

    cached = redis.get(cache_key)

    if cached:
        if normalized_query:
            search = SearchHistory(
                user_id=current_user.id,
                query=normalized_query,
                brand_id=brand_id,
                category_id=category_id,
                min_price=min_price,
                max_price=max_price,
            )

            db.add(search)
            db.commit()

        return json.loads(cached)

    # -----------------------------
    # 2. Query PostgreSQL
    # -----------------------------

    from sqlalchemy.orm import joinedload
    query = select(Product).options(joinedload(Product.category)).where(Product.available.is_(True))

    if normalized_query:
        search_term = f"%{normalized_query}%"

        query = query.where(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
            )
        )

    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    if brand_id is not None:
        query = query.where(Product.brand_id == brand_id)

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    query = query.order_by(Product.name.asc()).offset(offset).limit(limit)

    products = db.scalars(query).all()

    # -----------------------------
    # 3. Record search history
    # -----------------------------

    if normalized_query:
        search = SearchHistory(
            user_id=current_user.id,
            query=normalized_query,
            brand_id=brand_id,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
        )

        db.add(search)
        db.commit()

    # -----------------------------
    # 4. Convert response
    # -----------------------------

    response = [
        ProductResponse.model_validate(product).model_dump(mode="json")
        for product in products
    ]

    # -----------------------------
    # 5. Cache result
    # -----------------------------

    redis.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response),
    )

    return response


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from sqlalchemy.orm import joinedload
    product = db.scalar(
        select(Product).options(joinedload(Product.category)).where(
            Product.id == product_id,
            Product.available.is_(True),
        )
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product
