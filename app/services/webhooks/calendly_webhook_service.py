from app.schemas.webhooks import NormalizedBookingConfirmedEvent
from app.services.webhooks.payload_normalizers.calendly_payload_normalizer import (
    normalize_calendly_invitee_created_event,
)


def process_calendly_webhook(
    payload: dict,
) -> NormalizedBookingConfirmedEvent | None:
    """
    Process Calendly webhook payload.

    Business rules:
    - Webhook orchestration belongs to service layer.
    - This service coordinates normalization and future lifecycle handling.
    - Business lifecycle services must not consume raw provider payloads.

    Side effects:
    - None yet.
    - Lifecycle transitions will be added later.

    Invariants / restrictions:
    - Unsupported events must be ignored safely.
    """

    event_type = payload.get("event")

    if event_type == "invitee.created":
        return normalize_calendly_invitee_created_event(payload)

    return None