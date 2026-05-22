from unittest.mock import patch


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