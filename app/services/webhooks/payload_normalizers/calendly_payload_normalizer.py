from datetime import datetime, UTC

from app.schemas.webhooks import NormalizedBookingConfirmedEvent


def normalize_calendly_invitee_created_event(
    payload: dict,
) -> NormalizedBookingConfirmedEvent:
    """
    Normalize Calendly invitee.created webhook payload.

    Business rules:
    - Converts provider-specific Calendly payload into
      provider-agnostic internal webhook event.
    - Only normalization logic belongs here.
    - No entitlement lifecycle logic allowed.

    Side effects:
    - None.

    Invariants / restrictions:
    - Expects Calendly invitee.created payload shape.
    - Raises KeyError if required provider fields are missing.
    """

    event = payload["payload"]["event"]
    invitee = payload["payload"]["invitee"]

    return NormalizedBookingConfirmedEvent(
        provider="calendly",
        provider_event_uri=event["uri"],
        provider_invitee_uri=invitee["uri"],
        occurred_at=datetime.now(UTC),
    )