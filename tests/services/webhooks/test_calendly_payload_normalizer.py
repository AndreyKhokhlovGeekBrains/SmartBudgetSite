import pytest

from app.services.webhooks.payload_normalizers.calendly_payload_normalizer import (
    normalize_calendly_invitee_created_event,
)


def test_normalize_calendly_invitee_created_event():
    """
    Test case: Calendly payload normalization

    What we verify:
    - Calendly payload is converted into provider-agnostic event.
    - Required provider identifiers are extracted correctly.
    - Provider name is normalized consistently.

    Business rule:
    - Internal lifecycle services must consume normalized events,
      not raw Calendly payloads.
    """

    payload = {
        "payload": {
            "event": {
                "uri": "https://api.calendly.com/scheduled_events/ABC",
            },
            "invitee": {
                "uri": "https://api.calendly.com/invitees/XYZ",
            },
        },
    }

    normalized = normalize_calendly_invitee_created_event(payload)

    assert normalized.provider == "calendly"

    assert (
        normalized.provider_event_uri
        == "https://api.calendly.com/scheduled_events/ABC"
    )

    assert (
        normalized.provider_invitee_uri
        == "https://api.calendly.com/invitees/XYZ"
    )


def test_normalize_calendly_invitee_created_event_missing_event_uri():
    """
    Test case: Calendly payload missing required event URI

    What we verify:
    - Normalizer rejects malformed provider payloads.
    - Missing required provider identifiers raise KeyError.

    Business rule:
    - Lifecycle services must never receive incomplete normalized events.
    """

    payload = {
        "payload": {
            "event": {},
            "invitee": {
                "uri": "https://api.calendly.com/invitees/XYZ",
            },
        },
    }

    with pytest.raises(KeyError):
        normalize_calendly_invitee_created_event(payload)