from datetime import datetime

from pydantic import BaseModel


class NormalizedBookingConfirmedEvent(BaseModel):
    """
    Provider-agnostic normalized booking confirmation event.

    Business rules:
    - Internal services must consume normalized events instead of
      raw provider payloads.
    - This schema acts as a stable integration boundary between
      external webhook providers and internal lifecycle services.

    Side effects:
    - None. Pure transport/normalization schema.

    Invariants / restrictions:
    - provider_event_uri must uniquely identify the provider-side event.
    - occurred_at must represent provider event creation/confirmation time.
    """

    provider: str
    provider_event_uri: str
    provider_invitee_uri: str | None = None
    occurred_at: datetime