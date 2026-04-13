from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.models.product import Product


def test_admin_products_list_page_renders_products(
    client: TestClient,
    db_session: Any,
) -> None:
    """
    Verifies:
    - /admin/products returns 200
    - product list page renders saved products
    """

    product = Product(
        slug="smartbudget",
        name="SmartBudget",
        edition="Standard",
        version="1.0",
        price=49.0,
        status="in_sale",
    )
    db_session.add(product)
    db_session.commit()

    response = client.get("/admin/products")

    assert response.status_code == 200
    assert "SmartBudget" in response.text
    assert "Standard" in response.text
    assert "1.0" in response.text
    assert "in_sale" in response.text


