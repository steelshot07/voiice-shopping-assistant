from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    products = relationship(
        "Product",
        back_populates="brand",
    )

    search_history = relationship(
        "SearchHistory",
        back_populates="brand",
    )
