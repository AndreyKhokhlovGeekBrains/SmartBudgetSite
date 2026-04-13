from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.product import Product

from typing import cast


class ProductsRepository:
    """
    Repository for Product entity.

    Handles DB access for admin product management.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(self) -> list[Product]:
        """
        Return all products ordered by newest first.
        """
        result = (
            self.db.query(Product)
            .order_by(Product.id.desc())
            .all()
        )

        return cast(list[Product], result)