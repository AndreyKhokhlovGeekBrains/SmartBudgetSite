from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ProductQnA(Base):
    """
    Public product Q&A entity.

    Represents a curated user question and founder reply
    that can be displayed on product pages.
    """

    __tablename__ = "product_qna"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Link to product
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User question (from feedback)
    question: Mapped[str] = mapped_column(Text, nullable=False)

    # Founder/admin reply
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional display name (can be anonymized)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Publication flag
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
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