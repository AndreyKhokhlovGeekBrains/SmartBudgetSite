import hashlib
import hmac
import json

from unittest.mock import patch


def _build_calendly_signature_header(
    payload: bytes,
    signing_secret: str,
    timestamp: str = "1492774577",
) -> str:
    signed_payload = f"{timestamp}.".encode("utf-8") + payload

    signature = hmac.new(
        signing_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    return f"t={timestamp},v1={signature}"


def test_calendly_webhook_endpoint_accepts_post_request(client):
    """
    Test case: Calendly webhook endpoint skeleton

    What we verify:
    - The endpoint exists.
    - POST requests are accepted.
    - The temporary skeleton returns 204 No Content.

    Business rule:
    - The webhook route is only an integration boundary at this stage.
    - Signature verification and payload processing will be added in services later.
    """

    payload = {
        "event": "invitee.created",
        "payload": {
            "event": "https://api.calendly.com/scheduled_events/ABC",
            "invitee": "https://api.calendly.com/invitees/XYZ",
        },
    }

    payload_bytes = json.dumps(payload).encode("utf-8")

    signing_secret = "test-secret"

    signature_header = _build_calendly_signature_header(
        payload=payload_bytes,
        signing_secret=signing_secret,
    )

    response = client.post(
        "/v1/webhooks/calendly",
        json=payload,
        headers={
            "Calendly-Webhook-Signature": signature_header,
            "Calendly-Webhook-Signing-Secret": signing_secret,
        },
    )

    assert response.status_code == 204
    assert response.content == b""


def test_calendly_webhook_rejects_invalid_signature(client):
    """
    Test case: invalid Calendly webhook signature

    What we verify:
    - Invalid signature blocks request processing.
    - Webhook route returns 401.
    - Payload must not enter business processing when verification fails.

    Business rule:
    - Signature verification failure must stop webhook processing immediately.
    """

    with patch(
        "app.api.v1.webhooks.verify_webhook_signature",
        return_value=False,
    ):
        response = client.post(
            "/v1/webhooks/calendly",
            json={
                "event": "invitee.created",
                "payload": {
                    "event": {
                        "uri": "https://api.calendly.com/scheduled_events/ABC",
                    },
                    "invitee": {
                        "uri": "https://api.calendly.com/invitees/XYZ",
                    },
                },
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid webhook signature"


def test_calendly_webhook_rejects_unsigned_request(client):
    """
    Test case: unsigned Calendly webhook request.

    What we verify:
    - Request is rejected before orchestration layer execution.

    Business rule:
    - Unverified webhook requests must never enter
      reconciliation or lifecycle synchronization pipeline.
    """

    with patch(
        "app.services.webhooks.calendly_webhook_service.process_calendly_webhook"
    ) as mocked_process:

        response = client.post(
            "/v1/webhooks/calendly",
            json={"event": "invitee.created"},
        )

        assert response.status_code == 401

        mocked_process.assert_not_called()