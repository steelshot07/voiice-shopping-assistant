from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="en-IN",
        server_default="en-IN",
    )

    preferred_brands: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )

    preferred_categories: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="preferences",
    )
