from unittest.mock import patch

from app.models.consultation_entitlement import ConsultationEntitlementStatus
from tests.services.test_consultation_entitlement_service import (
    create_test_consultation_entitlement,
)

from app.services.webhooks.calendly_webhook_service import (
    process_calendly_webhook,
)


def test_process_calendly_webhook_invitee_created(db_session):
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

    result = process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    assert result is not None
    assert result.provider == "calendly"


def test_process_calendly_webhook_unsupported_event(db_session):
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

    result = process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    assert result is None


@patch(
    "app.services.webhooks.calendly_webhook_service.reconcile_booking_confirmed_event"
)
def test_process_calendly_webhook_calls_reconciliation(
    reconciliation_mock,
    db_session,
):
    """
    Test case: webhook orchestration triggers reconciliation.

    Business rules:
    - Webhook orchestration coordinates reconciliation.
    - Reconciliation must happen after normalization.
    - Lifecycle mutation is still outside orchestration at this stage.
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

    reconciliation_mock.return_value = None

    process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    reconciliation_mock.assert_called_once()


def test_process_calendly_webhook_handles_missing_entitlement_safely(
    db_session,
):
    """
    Test case: webhook reconciliation resolves no entitlement.

    Business rules:
    - Unknown provider events must not create entitlements.
    - Missing reconciliation target must be handled safely.
    - Webhook orchestration must remain replay-safe.
    """

    payload = {
        "event": "invitee.created",
        "payload": {
            "event": {
                "uri": "https://api.calendly.com/scheduled_events/UNKNOWN",
            },
            "invitee": {
                "uri": "https://api.calendly.com/invitees/UNKNOWN",
            },
        },
    }

    result = process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    assert result is not None
    assert result.provider_event_uri.endswith("UNKNOWN")


def test_process_calendly_webhook_marks_entitlement_as_booked(
    db_session,
):
    """
    Test case: webhook orchestration synchronizes entitlement lifecycle.

    Business rules:
    - Successful reconciliation triggers BOOKED transition.
    - Webhook orchestration delegates lifecycle mutation to lifecycle service.
    - Lifecycle synchronization must remain replay-safe.
    """

    entitlement = create_test_consultation_entitlement(db_session)

    entitlement.provider_event_uri = (
        "https://api.calendly.com/scheduled_events/BOOKING-1"
    )

    db_session.flush()

    payload = {
        "event": "invitee.created",
        "payload": {
            "event": {
                "uri": "https://api.calendly.com/scheduled_events/BOOKING-1",
            },
            "invitee": {
                "uri": "https://api.calendly.com/invitees/INVITEE-1",
            },
        },
    }

    process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    db_session.refresh(entitlement)

    assert entitlement.status == ConsultationEntitlementStatus.BOOKED
    assert entitlement.booking_provider == "calendly"
    assert entitlement.provider_invitee_uri.endswith("INVITEE-1")
    assert entitlement.booked_at is not None


def test_process_calendly_webhook_replay_is_idempotent(
    db_session,
):
    """
    Test case: duplicate webhook delivery is replay-safe.

    Business rules:
    - Providers may deliver the same webhook more than once.
    - Repeated booking confirmation must not fail.
    - BOOKED entitlement remains BOOKED after replay.
    """

    entitlement = create_test_consultation_entitlement(db_session)

    entitlement.provider_event_uri = (
        "https://api.calendly.com/scheduled_events/REPLAY-1"
    )

    db_session.flush()

    payload = {
        "event": "invitee.created",
        "payload": {
            "event": {
                "uri": "https://api.calendly.com/scheduled_events/REPLAY-1",
            },
            "invitee": {
                "uri": "https://api.calendly.com/invitees/REPLAY-INVITEE-1",
            },
        },
    }

    process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    process_calendly_webhook(
        db=db_session,
        payload=payload,
    )

    db_session.refresh(entitlement)

    assert entitlement.status == ConsultationEntitlementStatus.BOOKED
    assert entitlement.booking_provider == "calendly"
    assert entitlement.provider_event_uri.endswith("REPLAY-1")
    assert entitlement.provider_invitee_uri.endswith("REPLAY-INVITEE-1")
    assert entitlement.booked_at is not None


def test_process_calendly_webhook_logs_processed_event(db_session):
    """
    Test case: successful webhook processing audit logging.

    What we verify:
    - Successful webhook processing emits audit log event.

    Business rule:
    - Webhook lifecycle processing must remain observable.
    """

    payload = {
        "event": "invitee.created",
        "payload": {
            "event": "https://api.calendly.com/scheduled_events/ABC",
            "invitee": "https://api.calendly.com/invitees/XYZ",
        },
    }

    with patch(
        "app.services.webhooks.calendly_webhook_service.log_webhook_event"
    ) as mocked_log:

        process_calendly_webhook(
            db=db_session,
            payload=payload,
        )

        mocked_log.assert_called_once_with(
            provider="calendly",
            event_type="invitee.created",
            status="processed",
        )