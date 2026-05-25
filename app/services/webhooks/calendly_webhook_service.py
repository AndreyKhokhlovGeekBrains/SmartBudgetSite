from sqlalchemy.orm import Session

from app.schemas.webhooks import NormalizedBookingConfirmedEvent
from app.services.webhooks.payload_normalizers.calendly_payload_normalizer import (
    normalize_calendly_invitee_created_event,
)
from app.services.webhooks.reconciliation_service import (
    reconcile_booking_confirmed_event,
)
from app.services.consultation_entitlement_service import (
    mark_entitlement_as_booked,
)


def process_calendly_webhook(
    db: Session,
    payload: dict,
) -> NormalizedBookingConfirmedEvent | None:
    """
    Process Calendly webhook payload.

    Business rules:
    - Webhook orchestration belongs to service layer.
    - This service coordinates normalization and reconciliation.
    - Business lifecycle services must not consume raw provider payloads.

    Side effects:
    - Performs entitlement reconciliation lookup.
    - Lifecycle transitions are not applied yet.

    Invariants / restrictions:
    - Unsupported events must be ignored safely.
    """

    event_type = payload.get("event")

    if event_type == "invitee.created":
        normalized_event = normalize_calendly_invitee_created_event(payload)

        resolved_entitlement = reconcile_booking_confirmed_event(
            db=db,
            event=normalized_event,
        )

        if resolved_entitlement is None:
            return normalized_event

        mark_entitlement_as_booked(
            db=db,
            entitlement=resolved_entitlement,
            booking_provider=normalized_event.provider,
            provider_event_uri=normalized_event.provider_event_uri,
            provider_invitee_uri=normalized_event.provider_invitee_uri,
            booked_at=normalized_event.occurred_at,
        )

        return normalized_event

    return None


