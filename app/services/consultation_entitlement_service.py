from datetime import datetime, timedelta, UTC

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.consultation_entitlement import (
    ConsultationEntitlement,
    ConsultationEntitlementStatus,
)
from app.models.sale_item import SaleItem, SaleItemType


DEFAULT_CONSULTATION_BOOKING_WINDOW_DAYS = 14
CONSULTATION_SERVICE_TYPE = "consultation"


def create_consultation_entitlement(
    db: Session,
    sale_item: SaleItem,
) -> ConsultationEntitlement:
    """
    Create a backend-owned booking entitlement for a purchased consultation item.

    Business rules:
    - Only service sale items can receive consultation entitlements.
    - The linked service_addon must represent a consultation.
    - MVP allows only one entitlement per consultation sale item.
    - Booking access expires after the default booking window.

    Side effects:
    - Inserts a ConsultationEntitlement row.
    - Flushes the current DB session.
    - Returns the created entitlement.

    Invariants/restrictions:
    - Does not create a Calendly booking.
    - Does not expose provider-specific metadata.
    - Does not create entitlements for product sale items.
    """

    if sale_item.item_type != SaleItemType.SERVICE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation entitlement can only be created for service sale items.",
        )

    if sale_item.service_addon is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service sale item must have a linked service add-on.",
        )

    if sale_item.service_addon.service_type != CONSULTATION_SERVICE_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation entitlement can only be created for consultation services.",
        )

    if sale_item.consultation_entitlement is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Consultation entitlement already exists for this sale item.",
        )

    entitlement = ConsultationEntitlement(
        sale_item_id=sale_item.id,
        status=ConsultationEntitlementStatus.AVAILABLE.value,
        expires_at=(
                datetime.now(UTC)
                + timedelta(days=DEFAULT_CONSULTATION_BOOKING_WINDOW_DAYS)
        ),
    )

    sale_item.consultation_entitlement = entitlement

    db.add(entitlement)
    db.flush()

    return entitlement


def _ensure_utc_aware(value: datetime) -> datetime:
    """
    Convert SQLite/PostgreSQL datetime value to UTC-aware datetime.

    Business rules:
    - Naive values are treated as UTC.
    - Aware values are preserved.

    Side effects:
    - None.

    Invariants/restrictions:
    - This helper does not change stored database values.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value


def get_valid_consultation_entitlement_by_token(
    db: Session,
    booking_token: str,
) -> ConsultationEntitlement:
    """
    Validate consultation booking token and return an active entitlement.

    Business rules:
    - Token must exist.
    - Entitlement must be available.
    - Entitlement must not be expired.
    - Booked, cancelled, and expired entitlements must not allow booking access.

    Side effects:
    - Does not modify the database.
    - Does not create a Calendly booking.

    Invariants/restrictions:
    - This function only validates backend-owned access rights.
    - Booking provider access must be shown only after this validation passes.
    """

    entitlement: ConsultationEntitlement | None = (
        db.query(ConsultationEntitlement)
        .filter(ConsultationEntitlement.booking_token == booking_token)
        .one_or_none()
    )

    if entitlement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation booking link was not found.",
        )

    if entitlement.status != ConsultationEntitlementStatus.AVAILABLE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consultation booking link is no longer available.",
        )

    if _ensure_utc_aware(entitlement.expires_at) <= datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consultation booking link has expired.",
        )

    return entitlement


