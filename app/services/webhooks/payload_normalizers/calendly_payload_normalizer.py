from datetime import datetime, UTC

from app.schemas.webhooks import NormalizedBookingConfirmedEvent


def _extract_uri(value):
    """
    Extract URI from Calendly payload field.

    Business rules:
    - Calendly webhook payload may provide provider identifiers either
      as plain URI strings or as objects containing a "uri" key.
    - Normalized internal events must always receive plain URI strings.

    Raises:
    - KeyError when required URI is missing.
    - TypeError when payload shape is unsupported.
    """

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return value["uri"]

    raise TypeError("Unsupported Calendly URI payload field shape.")


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

    return NormalizedBookingConfirmedEvent(
        provider="calendly",
        provider_event_uri=_extract_uri(payload["payload"]["event"]),
        provider_invitee_uri = _extract_uri(payload["payload"]["invitee"]),
        occurred_at=datetime.now(UTC),
    )