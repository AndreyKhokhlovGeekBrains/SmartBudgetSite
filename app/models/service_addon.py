from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ServiceAddon(Base):
    """
    Service/add-on available for checkout.

    Business rules:
    - Service add-ons are not downloadable product SKUs.
    - Add-ons can be attached to product checkout later.
    - Consultation price must come from DB, not from hard-coded checkout logic.

    Side effects:
    - None. This model only describes persisted add-on data.

    Invariants/restrictions:
    - code is unique and stable, e.g. consultation_1h.
    - amount must be non-negative.
    - currency_code is stored as ISO-like uppercase 3-letter code.
    """

    __tablename__ = "service_addons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    service_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    family_slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    package_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_service_addons_amount_non_negative"),
    )