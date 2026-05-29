"""
Webhook audit status constants.

Business rules:
- Audit status values must stay consistent across webhook routes and services.
- These constants describe processing outcomes, not business lifecycle states.

Side effects:
- None.

Invariants / restrictions:
- Do not put provider-specific logic here.
- Do not store secrets, payloads, or headers here.
"""

WEBHOOK_STATUS_PROCESSED = "processed"
WEBHOOK_STATUS_REJECTED = "rejected"
WEBHOOK_STATUS_IGNORED = "ignored"
WEBHOOK_STATUS_MALFORMED_PAYLOAD = "malformed_payload"
WEBHOOK_STATUS_RECONCILIATION_MISMATCH = "reconciliation_mismatch"