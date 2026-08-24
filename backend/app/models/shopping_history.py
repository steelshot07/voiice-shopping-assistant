from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ShoppingHistory(Base):
    __tablename__ = "shopping_history"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        init=False,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    product = relationship(
        "Product",
        back_populates="shopping_history",
    )

    user = relationship(
        "User",
        back_populates="shopping_history",
    )
