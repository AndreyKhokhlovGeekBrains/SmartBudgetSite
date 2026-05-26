import logging


logger = logging.getLogger(__name__)


def log_webhook_event(
    provider: str,
    event_type: str,
    status: str,
) -> None:
    """
    Log webhook processing lifecycle event.

    Business rules:
    - Webhook observability must remain centralized.
    - Audit logging must not contain sensitive secrets.

    Side effects:
    - Writes structured webhook lifecycle logs.

    Invariants / restrictions:
    - Signing secrets must never be logged.
    - Raw payload bodies should not be logged at INFO level.
    """

    logger.info(
        "Webhook event processed",
        extra={
            "provider": provider,
            "event_type": event_type,
            "status": status,
        },
    )