from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.core.db import Base

from app.models.product_price import ProductPrice

ALLOWED_EDITIONS = {"Standard", "Pro"}
ALLOWED_PRODUCT_STATUSES = {"in_sale", "in_development", "discontinued"}


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("slug", "edition", "version", name="uq_products_slug_edition_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Product family identifier used to group related SKUs.
    # Example: smartbudget
    family_slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    # Stable identifier for URLs / internal references
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    # Public product name, e.g. SmartBudget
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Path to the downloadable product archive
    archive_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Product edition / variant, e.g. Standard, Pro
    edition: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Semantic or business version, e.g. 1.0
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Release date can be empty for products still in development
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Related price records (history + multiple currencies support)
    prices: Mapped[list["ProductPrice"]] = relationship(
        "ProductPrice",
        backref="product",
        cascade="all, delete-orphan",
    )

    # Examples: in_sale, in_development, discontinued
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

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

    @validates("edition")
    def validate_edition(self, key, value):
        if value not in ALLOWED_EDITIONS:
            raise ValueError(f"Invalid edition: {value}")
        return value

    @validates("status")
    def validate_status(self, key, value):
        if value not in ALLOWED_PRODUCT_STATUSES:
            raise ValueError(f"Invalid status: {value}")
        return value

