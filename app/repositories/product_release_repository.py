from __future__ import annotations
from sqlalchemy.orm import Session

from app.models.product_release import ProductRelease


class ProductReleaseRepository:
    """
    Repository for ProductRelease entity.

    Handles DB access for product release management.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_product_id(self, product_id: int) -> list[ProductRelease]:
        return (
            self.db.query(ProductRelease)
            .filter(ProductRelease.product_id == product_id)
            .order_by(ProductRelease.created_at.desc(), ProductRelease.id.desc())
            .all()
        )

    def get_by_id(self, release_id: int) -> ProductRelease | None:
        return (
            self.db.query(ProductRelease)
            .filter(ProductRelease.id == release_id)
            .first()
        )

    def get_active_by_product_id(self, product_id: int) -> ProductRelease | None:
        return (
            self.db.query(ProductRelease)
            .filter(ProductRelease.product_id == product_id)
            .filter(ProductRelease.is_active.is_(True))
            .first()
        )

    def create(self, release: ProductRelease) -> ProductRelease:
        self.db.add(release)
        self.db.flush()
        return release