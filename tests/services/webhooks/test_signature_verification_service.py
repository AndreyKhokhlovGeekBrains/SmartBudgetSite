from app.services.webhooks.signature_verification_service import (
    verify_webhook_signature,
)


def test_verify_webhook_signature_accepts_supported_provider():
    """
    Test case: supported webhook provider

    What we verify:
    - Calendly provider is accepted by current verification scaffold.

    Business rule:
    - Signature verification must be explicit before webhook processing.
    """

    result = verify_webhook_signature(
        provider="calendly",
        payload=b"{}",
        headers={},
    )

    assert result is True


def test_verify_webhook_signature_rejects_unsupported_provider():
    """
    Test case: unsupported webhook provider

    What we verify:
    - Unknown providers are rejected safely.

    Business rule:
    - Unsupported webhook providers must not enter processing pipeline.
    """

    result = verify_webhook_signature(
        provider="unknown",
        payload=b"{}",
        headers={},
    )

    assert result is False