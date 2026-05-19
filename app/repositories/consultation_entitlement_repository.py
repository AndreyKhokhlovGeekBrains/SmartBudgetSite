from sqlalchemy.orm import Session

from app.models.consultation_entitlement import ConsultationEntitlement


class ConsultationEntitlementRepository:
    """
    Repository for consultation entitlement persistence queries.

    Business rules:
    - Repository only loads entitlement data.
    - Booking lifecycle decisions belong to service layer.

    Side effects:
    - Executes read queries against the database.

    Invariants/restrictions:
    - Do not place status transition logic here.
    """

    @staticmethod
    def get_by_provider_event_uri(
        db: Session,
        provider_event_uri: str,
    ) -> ConsultationEntitlement | None:
        """
        Find consultation entitlement by external provider event URI.

        Business rules:
        - Used for future webhook reconciliation.
        - Provider event URI should identify the external booking event.

        Side effects:
        - Executes one database query.

        Invariants/restrictions:
        - Does not validate status.
        - Does not mutate entitlement.
        """

        return (
            db.query(ConsultationEntitlement)
            .filter(
                ConsultationEntitlement.provider_event_uri == provider_event_uri,
            )
            .one_or_none()
        )