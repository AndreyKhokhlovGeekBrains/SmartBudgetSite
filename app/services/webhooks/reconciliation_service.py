from app.models.consultation_entitlement import ConsultationEntitlement
from app.repositories.consultation_entitlement_repository import (
    ConsultationEntitlementRepository,
)
from app.schemas.webhooks import (
    NormalizedBookingConfirmedEvent,
)


def reconcile_booking_confirmed_event(
    db,
    event: NormalizedBookingConfirmedEvent,
) -> ConsultationEntitlement | None:
    """
    Resolve provider booking event into existing entitlement.

    Business rules:
    - webhook events must never create entitlements
    - reconciliation is provider-event driven
    - missing entitlement is handled safely
    - lifecycle transitions are NOT applied yet

    Returns:
        ConsultationEntitlement | None
    """

    entitlement = (
        ConsultationEntitlementRepository.get_by_provider_event_uri(
            db=db,
            provider_event_uri=event.provider_event_uri,
        )
    )

    return entitlement