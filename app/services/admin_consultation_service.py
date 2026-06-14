from sqlalchemy.orm import Session

from app.models.consultation_entitlement import ConsultationEntitlement
from app.repositories.consultation_entitlement_repository import (
    ConsultationEntitlementRepository,
)


def get_consultation_entitlements(
    db: Session,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ConsultationEntitlement]:
    """
    Load consultation entitlements for admin visibility.

    Business rules:
    - Admin visibility is read-only.
    - Optional status filter is used only for admin operational visibility.
    - Lifecycle mutations belong to dedicated business services.

    Side effects:
    - Executes repository read query.

    Invariants/restrictions:
    - Does not mutate entitlement lifecycle state.
    - Does not apply booking provider logic.
    """

    return ConsultationEntitlementRepository.get_all_with_sale_data(
        db=db,
        status=status,
        limit=limit,
        offset=offset,
    )