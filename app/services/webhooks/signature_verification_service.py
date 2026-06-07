import hashlib
import hmac
from collections.abc import Mapping
from app.core.config import settings


CALENDLY_SIGNATURE_HEADER = "Calendly-Webhook-Signature"
CALENDLY_SIGNING_SECRET_HEADER = "Calendly-Webhook-Signing-Secret"


def verify_webhook_signature(
    provider: str,
    payload: bytes,
    headers: Mapping[str, str],
) -> bool:
    """
    Verify webhook signature for external provider.
    """

    if provider == "calendly":
        return _verify_calendly_signature(payload=payload, headers=headers)

    return False


def _verify_calendly_signature(
    payload: bytes,
    headers: Mapping[str, str],
) -> bool:
    signature_header = headers.get(CALENDLY_SIGNATURE_HEADER)
    signing_secret = settings.CALENDLY_WEBHOOK_SIGNING_SECRET

    if not signature_header or not signing_secret:
        return False

    try:
        timestamp, provided_signature = _parse_calendly_signature_header(
            signature_header
        )
    except ValueError:
        return False

    signed_payload = f"{timestamp}.".encode("utf-8") + payload

    expected_signature = hmac.new(
        signing_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, provided_signature)


def _parse_calendly_signature_header(signature_header: str) -> tuple[str, str]:
    parts = dict(
        item.split("=", maxsplit=1)
        for item in signature_header.split(",")
        if "=" in item
    )

    timestamp = parts.get("t")
    signature = parts.get("v1")

    if not timestamp or not signature:
        raise ValueError("Invalid Calendly signature header.")

    return timestamp, signature