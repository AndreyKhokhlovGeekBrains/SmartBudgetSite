from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import PaymentStatus
from app.models.product import Product
from app.models.sale import Sale


def get_verified_purchases_by_email(
    db: Session,
    email: str,
) -> list[dict]:
    normalized_email = email.strip().lower()

    stmt = (
        select(
            Sale.id.label("sale_id"),
            Sale.product_id,
            Product.name.label("product_name"),
            Product.slug.label("product_slug"),
            Product.edition,
            Sale.created_at,
        )
        .join(Product, Product.id == Sale.product_id)
        .where(
            Sale.customer_email == normalized_email,
            Sale.payment_status == PaymentStatus.PAID,
        )
        .order_by(Sale.created_at.desc(), Sale.id.desc())
    )

    rows = db.execute(stmt).all()

    return [
        {
            "sale_id": row.sale_id,
            "product_id": row.product_id,
            "product_name": row.product_name,
            "product_slug": row.product_slug,
            "edition": row.edition,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def is_verified_sale_for_email(
    db: Session,
    sale_id: int,
    email: str,
) -> bool:
    normalized_email = email.strip().lower()

    stmt = select(Sale.id).where(
        Sale.id == sale_id,
        Sale.customer_email == normalized_email,
        Sale.payment_status == PaymentStatus.PAID,
    )

    return db.execute(stmt).first() is not None