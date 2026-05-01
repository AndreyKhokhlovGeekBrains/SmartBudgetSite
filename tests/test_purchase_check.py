import pytest

def test_check_purchase_not_found(client):
    """
    Test case: purchase lookup for unknown email

    What we verify:
    - Endpoint /v1/check-purchase is reachable
    - For an email with no purchases:
        -> verified = False
        -> purchases list is empty
    """

    response = client.post(
        "/v1/check-purchase",
        json={"email": "unknown@example.com"}
    )

    # Check HTTP response status
    assert response.status_code == 200

    data = response.json()

    # No purchases should be found
    assert data["verified"] is False
    assert data["purchases"] == []

def test_check_purchase_verified(client, db_session):
    """
    Test case: purchase lookup for existing customer

    What we verify:
    - If a purchase exists for the given email:
        -> verified = True
        -> purchases list contains the expected item
    """

    from app.models.sale import Sale
    from app.models.product import Product
    from datetime import datetime, UTC

    # Create test product
    product = Product(
        family_slug="smartbudget",
        slug="smartbudget",
        name="SmartBudget",
        edition="Standard",
        version="1.0",
        status="in_sale",
        archive_path="test/path.zip",
    )

    db_session.add(product)
    db_session.flush()  # get product.id

    # Create test sale
    sale = Sale(
        product_id=product.id,
        customer_email="buyer@example.com",
        amount=10.00,
        currency="EUR",
        payment_status="paid",
        created_at=datetime.now(UTC)
    )

    db_session.add(sale)
    db_session.commit()

    # Call API
    response = client.post(
        "/v1/check-purchase",
        json={"email": "buyer@example.com"}
    )

    assert response.status_code == 200

    data = response.json()

    # Verify result
    assert data["verified"] is True
    assert len(data["purchases"]) == 1

    purchase = data["purchases"][0]

    assert purchase["product_name"] == "SmartBudget"
    assert purchase["sale_id"] == sale.id

def test_check_purchase_empty_email(client):
    """
    Test case: empty email input

    What we verify:
    - API should reject empty email
    - Returns validation error (422)
    """

    response = client.post(
        "/v1/check-purchase",
        json={"email": ""}
    )

    assert response.status_code == 422

def test_product_invalid_edition(db_session):
    """
    Test case: product creation with invalid edition

    What we verify:
    - Creating a Product with unsupported edition raises ValueError
    """

    from app.models.product import Product

    try:
        product = Product(
            family_slug="smartbudget",
            slug="smartbudget-invalid",
            name="SmartBudget",
            edition="InvalidEdition",
            version="1.0",
            status="in_sale",
            archive_path="test/path.zip",
        )
        db_session.add(product)
        db_session.flush()

        assert False, "Expected ValueError was not raised"

    except ValueError as e:
        assert "Invalid edition" in str(e)


def test_check_purchase_returns_product_item_type(client, db_session):
    """
    Test case: purchase lookup returns product item type

    What we verify:
    - Product purchase is marked as verified
    - Returned purchase item contains item_type = product
    """

    from datetime import UTC, datetime

    from app.models.enums import PaymentStatus
    from app.models.product import Product
    from app.models.sale import Sale

    product = Product(
        family_slug="smartbudget",
        slug="smartbudget-ru-standard",
        name="SmartBudget RU Standard",
        edition="Standard",
        version="1.0",
        status="in_sale",
        archive_path="test/path.zip",
    )
    db_session.add(product)
    db_session.flush()

    sale = Sale(
        product_id=product.id,
        customer_email="customer@example.com",
        amount=39,
        currency="EUR",
        payment_status=PaymentStatus.PAID,
        created_at=datetime.now(UTC),
    )
    db_session.add(sale)
    db_session.commit()

    response = client.post(
        "/v1/check-purchase",
        json={"email": "customer@example.com"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["verified"] is True
    assert len(data["purchases"]) == 1
    assert data["purchases"][0]["item_type"] == "product"


@pytest.mark.xfail(reason="Service-only purchases not supported yet (no sale_items)")
def test_check_purchase_not_verified_for_service_only(client, db_session):
    """
    Test case: service-only purchase should not mark user as verified

    What we verify:
    - If user has only service purchases (no product)
      -> verified = False
    """

    from datetime import UTC, datetime

    from app.models.enums import PaymentStatus
    from app.models.product import Product
    from app.models.sale import Sale

    # Create product (needed for FK, but not used as purchase)
    product = Product(
        family_slug="smartbudget",
        slug="smartbudget-ru-standard",
        name="SmartBudget RU Standard",
        edition="Standard",
        version="1.0",
        status="in_sale",
        archive_path="test/path.zip",
    )
    db_session.add(product)
    db_session.flush()

    # Simulate service-only purchase (for now still uses Sale model)
    sale = Sale(
        product_id=product.id,  # временно, пока нет sale_items
        customer_email="service_only@example.com",
        amount=35,
        currency="EUR",
        payment_status=PaymentStatus.PAID,
        created_at=datetime.now(UTC),
    )
    db_session.add(sale)
    db_session.commit()

    response = client.post(
        "/v1/check-purchase",
        json={"email": "service_only@example.com"},
    )

    assert response.status_code == 200

    data = response.json()

    # 🔴 ВАЖНО: сейчас тест упадёт — и это нормально
    # потому что у нас пока нет разделения product/service в БД

    assert data["verified"] is False