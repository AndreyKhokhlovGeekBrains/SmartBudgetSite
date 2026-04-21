from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.product import Product
from sqlalchemy import and_, or_
from app.models.product_price import ProductPrice


class ProductsRepository:
    """
    Repository for Product entity.

    Handles DB access for admin product management.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(self):
        result = (
            self.db.query(Product, ProductPrice)
            .outerjoin(
                ProductPrice,
                and_(
                    ProductPrice.product_id == Product.id,
                    ProductPrice.is_active == True,
                    ProductPrice.currency_code.in_(["RUB", "EUR"]),
                ),
            )
            .order_by(Product.id.desc())
            .all()
        )

        return result