from sqlalchemy.orm import Session

from app.models.consultation_entitlement import ConsultationEntitlement
from app.repositories.consultation_entitlement_repository import (
    ConsultationEntitlementRepository,
)


def get_consultation_entitlements(
    db: Session,
) -> list[ConsultationEntitlement]:
    """
    Load consultation entitlements for admin visibility.

    Business rules:
    - Admin visibility is read-only.
    - Lifecycle mutations belong to dedicated business services.

    Side effects:
    - Executes repository read query.

    Invariants/restrictions:
    - Does not mutate entitlement lifecycle state.
    - Does not apply booking provider logic.
    """

    return ConsultationEntitlementRepository.get_all_with_sale_data(
        db=db,
    )