from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import PaymentStatus
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


def get_verified_purchases_by_email(
    db: Session,
    email: str,
) -> list[dict]:
    normalized_email = email.strip().lower()

    stmt = (
        select(
            Sale.id.label("sale_id"),
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.slug.label("product_slug"),
            Product.edition,
            Sale.created_at,
        )
        .join(SaleItem, SaleItem.sale_id == Sale.id)
        .join(Product, Product.id == SaleItem.product_id)
        .where(
            Sale.customer_email == normalized_email,
            Sale.payment_status == PaymentStatus.PAID,
            SaleItem.item_type == "product",
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
            "item_type": "product",
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


def list_admin_sales(
    db: Session,
    status: str | None = None,
    limit: int = 50,
) -> list[Sale]:
    """
    Return recent sales with purchased items for admin backoffice.

    Business rules:
    - Admin sales view starts as read-only operational visibility.
    - Sale is an order header.
    - SaleItem rows are the source of truth for purchased products/services.
    - Newest sales are shown first.
    - MVP list is intentionally limited to avoid loading unbounded history.

    Side effects:
    - None. Read-only query.

    Invariants / restrictions:
    - Does not mutate payment or fulfillment state.
    - Does not perform search/filtering yet.
    - Legacy sales.product_id must not be used for ownership display.
    """

    stmt = (
        select(Sale)
        .options(selectinload(Sale.items))
    )

    if status:
        stmt = stmt.where(Sale.payment_status == status)

    stmt = (
        stmt
        .order_by(Sale.created_at.desc(), Sale.id.desc())
        .limit(limit)
    )

    return list(db.execute(stmt).scalars().all())