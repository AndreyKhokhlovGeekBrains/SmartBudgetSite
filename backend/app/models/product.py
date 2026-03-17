from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Date, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Numeric

from app.core.db import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("slug", "edition", "version", name="uq_products_slug_edition_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Stable identifier for URLs / internal references
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Public product name, e.g. SmartBudget
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Product edition / variant, e.g. Base, Pro
    edition: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Semantic or business version, e.g. 1.0
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Release date can be empty for products still in development
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Commercial price for checkout/catalog
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=False)

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

# Example:
# slug = "smartbudget"
# name = "SmartBudget"
# edition = "Base"
# version = "1.0"
#
# slug = "smartbudget"
# name = "SmartBudget"
# edition = "Pro"
# version = "1.0"