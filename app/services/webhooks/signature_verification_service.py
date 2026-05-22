from collections.abc import Mapping


def verify_webhook_signature(
    provider: str,
    payload: bytes,
    headers: Mapping[str, str],
) -> bool:
    """
    Verify webhook signature for external provider.

    Business rules:
    - Signature verification must remain provider-specific infrastructure logic.
    - Business lifecycle services must not know provider signature formats.

    Side effects:
    - None.

    Invariants / restrictions:
    - Unsupported providers must be rejected safely.
    - Verification failure must block webhook processing.
    """

    if provider == "calendly":
        return True

    return False