from decimal import Decimal

from pydantic import BaseModel, Field


class VoiceCommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)
    context: dict | None = None
    confirmed: bool = False


class ProductOption(BaseModel):
    id: int
    name: str
    category: str | None = None
    price: str | None = None
    unit: str | None = None


class VoiceItemResult(BaseModel):
    product_name: str
    product_id: int | None = None
    quantity: float | None = None
    unit: str | None = None
    status: str  # "success", "ambiguous", "not_found", "error"
    message: str
    options: list[ProductOption] | None = None


class VoiceCommandResponse(BaseModel):
    intent: str
    status: str  # "success", "ambiguous", "clarification_needed", "confirmation_needed", "error", "unknown"
    message: str
    items: list[VoiceItemResult] = Field(default_factory=list)
    confidence: float = 0.0
    transcript: str = ""
    suggestion: str | None = None
    confirmation_required: bool = False
    context: dict | None = None