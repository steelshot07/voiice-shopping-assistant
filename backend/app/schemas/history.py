from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    brand_id: int | None
    category_id: int | None
    min_price: Decimal | None
    max_price: Decimal | None
    searched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShoppingHistoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit: str | None
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)
