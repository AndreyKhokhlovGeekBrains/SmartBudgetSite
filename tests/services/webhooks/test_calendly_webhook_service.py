from app.services.webhooks.calendly_webhook_service import (
    process_calendly_webhook,
)


def test_process_calendly_webhook_invitee_created():
    """
    Test case: supported Calendly webhook event

    What we verify:
    - Supported Calendly event is normalized successfully.
    - invitee.created is routed correctly.

    Business rule:
    - Event routing belongs to webhook orchestration layer.
    """

    payload = {
        "event": "invitee.created",
        "payload": {
            "event": {
                "uri": "https://api.calendly.com/scheduled_events/ABC",
            },
            "invitee": {
                "uri": "https://api.calendly.com/invitees/XYZ",
            },
        },
    }

    result = process_calendly_webhook(payload)

    assert result is not None
    assert result.provider == "calendly"


def test_process_calendly_webhook_unsupported_event():
    """
    Test case: unsupported Calendly webhook event

    What we verify:
    - Unsupported events are ignored safely.
    - No normalization happens for unknown event types.

    Business rule:
    - Unsupported provider events must not break webhook processing.
    """

    payload = {
        "event": "unknown.event",
        "payload": {},
    }

    result = process_calendly_webhook(payload)

    assert result is None