# tests/test_purchase_check.py

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
        slug="smartbudget",
        name="SmartBudget",
        edition="Standard",
        version="1.0",
        price=10.00,
        status="active"
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
            slug="smartbudget-invalid",
            name="SmartBudget",
            edition="InvalidEdition",  # not in ALLOWED_EDITIONS
            version="1.0",
            price=10.00,
            status="active"
        )
        db_session.add(product)
        db_session.flush()

        assert False, "Expected ValueError was not raised"

    except ValueError as e:
        assert "Invalid edition" in str(e)