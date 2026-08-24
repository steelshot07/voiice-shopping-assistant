from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductResponse


class ShoppingItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)
    unit: str | None = None


class ShoppingItemUpdate(BaseModel):
    quantity: Decimal | None = Field(default=None, gt=0)
    unit: str | None = None
    completed: bool | None = None


class ShoppingItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit: str | None
    completed: bool
    product: ProductResponse | None = None

    model_config = ConfigDict(from_attributes=True)
