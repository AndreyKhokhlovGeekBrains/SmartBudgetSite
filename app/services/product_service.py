from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.product_price import ProductPrice
from fastapi import HTTPException
from app.models.product import Product

ALLOWED_CURRENCIES = {"RUB", "EUR"}


def set_product_price(db: Session, product_id: int, currency_code: str, amount: Decimal):
    """
    Set a new price for a product.

    Rules:
    - deactivate previous active price for the same product and currency
    - create new active price record
    """

    currency_code = currency_code.upper().strip()

    if currency_code not in ALLOWED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported currency: {currency_code}",
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Price amount must be greater than zero",
        )

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product not found: {product_id}",
        )

    # Deactivate previous active price
    db.query(ProductPrice).filter(
        ProductPrice.product_id == product_id,
        ProductPrice.currency_code == currency_code,
        ProductPrice.is_active == True,
    ).update(
        {ProductPrice.is_active: False},
        synchronize_session=False,
    )

    # Insert new price
    new_price = ProductPrice(
        product_id=product_id,
        currency_code=currency_code,
        amount=amount,
        is_active=True,
    )

    db.add(new_price)
    db.commit()
    db.refresh(new_price)

    return new_price