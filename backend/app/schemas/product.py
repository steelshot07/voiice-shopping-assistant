from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    id: int
    name: str
    brand_id: int
    category_id: int
    category_name: str | None = None
    description: str | None
    size_value: Decimal | None
    size_unit: str | None
    price: Decimal
    currency: str
    image_url: str | None
    available: bool

    model_config = ConfigDict(from_attributes=True)


class ProductSearchParams(BaseModel):
    q: str = Field(min_length=1, max_length=100)
    brand_id: int | None = None
    category_id: int | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
