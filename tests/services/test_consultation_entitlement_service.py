import pytest
from fastapi import HTTPException
from app.services.sale_service import create_product_sale
from decimal import Decimal
from datetime import timedelta, UTC, datetime

from app.models.consultation_entitlement import ConsultationEntitlementStatus
from app.models.service_addon import ServiceAddon
from app.models.product import Product
from app.services.consultation_entitlement_service import (
    DEFAULT_CONSULTATION_BOOKING_WINDOW_DAYS,
    create_consultation_entitlement,
    get_valid_consultation_entitlement_by_token,
)
from app.services.sale_service import create_standalone_service_sale


def test_create_consultation_entitlement_for_consultation_service_item(db_session):
    """
    Test case: create consultation entitlement for purchased consultation service item.

    What we verify:
    - Entitlement is created for the correct sale item.
    - Status is available.
    - Booking token is generated.
    - Expiration date is populated.
    - ORM relationship between sale item and entitlement works.
    """

    service_addon = ServiceAddon(
        code="consultation_1h_int_standalone_test",
        name="1:1 SmartBudget consultation",
        service_type="consultation",
        usage_type="standalone",
        family_slug="smartbudget",
        package_code="INT",
        currency_code="EUR",
        amount=Decimal("79.00"),
        is_active=True,
    )
    db_session.add(service_addon)
    db_session.flush()

    sale = create_standalone_service_sale(
        db=db_session,
        service_addon_id=service_addon.id,
        service_name=service_addon.name,
        customer_email="customer@example.com",
        amount=service_addon.amount,
        currency=service_addon.currency_code,
    )
    db_session.flush()

    sale_item = sale.items[0]

    entitlement = create_consultation_entitlement(
        db=db_session,
        sale_item=sale_item,
    )

    actual_delta = entitlement.expires_at - entitlement.created_at

    assert actual_delta >= timedelta(days=DEFAULT_CONSULTATION_BOOKING_WINDOW_DAYS) - timedelta(seconds=1)
    assert actual_delta <= timedelta(days=DEFAULT_CONSULTATION_BOOKING_WINDOW_DAYS) + timedelta(seconds=1)

    assert entitlement.id is not None
    assert entitlement.sale_item_id == sale_item.id
    assert entitlement.status == ConsultationEntitlementStatus.AVAILABLE.value
    assert entitlement.booking_token is not None
    assert len(entitlement.booking_token) == 36
    assert entitlement.expires_at is not None

    assert sale_item.consultation_entitlement == entitlement


def test_create_consultation_entitlement_rejects_product_sale_item(db_session):
    """
    Test case: reject entitlement creation for product sale item.

    What we verify:
    - Product sale items cannot receive consultation entitlements.
    - Service raises HTTP 400.
    """

    product = Product(
        family_slug="smartbudget",
        slug="smartbudget-int-standard-entitlement-reject-test",
        name="SmartBudget",
        edition="Standard",
        version="1.0",
        archive_path="downloads/smartbudget-int-standard.zip",
        status="in_sale",
    )
    db_session.add(product)
    db_session.flush()

    sale = create_product_sale(
        db=db_session,
        product=product,
        customer_email="customer@example.com",
        amount=Decimal("39.00"),
        currency="EUR",
    )
    db_session.flush()

    sale_item = sale.items[0]

    with pytest.raises(HTTPException) as exc_info:
        create_consultation_entitlement(
            db=db_session,
            sale_item=sale_item,
        )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "Consultation entitlement can only be created for service sale items."
    )


def test_create_consultation_entitlement_rejects_duplicate_creation(db_session):
    """
    Test case: reject duplicate entitlement creation for the same consultation sale item.

    What we verify:
    - One consultation sale item may have only one entitlement.
    - Second entitlement creation attempt raises HTTP 409.
    """

    service_addon = ServiceAddon(
        code="consultation_1h_int_duplicate_test",
        name="1:1 SmartBudget consultation",
        service_type="consultation",
        usage_type="standalone",
        family_slug="smartbudget",
        package_code="INT",
        currency_code="EUR",
        amount=Decimal("79.00"),
        is_active=True,
    )
    db_session.add(service_addon)
    db_session.flush()

    sale = create_standalone_service_sale(
        db=db_session,
        service_addon_id=service_addon.id,
        service_name=service_addon.name,
        customer_email="customer@example.com",
        amount=service_addon.amount,
        currency=service_addon.currency_code,
    )
    db_session.flush()

    sale_item = sale.items[0]

    create_consultation_entitlement(
        db=db_session,
        sale_item=sale_item,
    )

    with pytest.raises(HTTPException) as exc_info:
        create_consultation_entitlement(
            db=db_session,
            sale_item=sale_item,
        )

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail
        == "Consultation entitlement already exists for this sale item."
    )


def test_get_valid_consultation_entitlement_by_token_returns_entitlement(
    db_session,
):
    """
    Test case: validate active consultation booking token.

    What we verify:
    - Existing available token returns entitlement.
    - Returned entitlement matches created entitlement.
    """

    service_addon = ServiceAddon(
        code="consultation_1h_int_token_test",
        name="1:1 SmartBudget consultation",
        service_type="consultation",
        usage_type="standalone",
        family_slug="smartbudget",
        package_code="INT",
        currency_code="EUR",
        amount=Decimal("79.00"),
        is_active=True,
    )
    db_session.add(service_addon)
    db_session.flush()

    sale = create_standalone_service_sale(
        db=db_session,
        service_addon_id=service_addon.id,
        service_name=service_addon.name,
        customer_email="customer@example.com",
        amount=service_addon.amount,
        currency=service_addon.currency_code,
    )
    db_session.flush()

    sale_item = sale.items[0]

    entitlement = create_consultation_entitlement(
        db=db_session,
        sale_item=sale_item,
    )

    result = get_valid_consultation_entitlement_by_token(
        db=db_session,
        booking_token=entitlement.booking_token,
    )

    assert result.id == entitlement.id
    assert result.booking_token == entitlement.booking_token
    assert (
        result.status
        == ConsultationEntitlementStatus.AVAILABLE.value
    )


def test_get_valid_consultation_entitlement_by_token_rejects_unknown_token(
    db_session,
):
    """
    Test case: reject unknown consultation booking token.

    What we verify:
    - Unknown token does not grant booking access.
    - Service raises HTTP 404.
    """

    with pytest.raises(HTTPException) as exc_info:
        get_valid_consultation_entitlement_by_token(
            db=db_session,
            booking_token="00000000-0000-0000-0000-000000000000",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Consultation booking link was not found."


def test_get_valid_consultation_entitlement_by_token_rejects_expired_token(
    db_session,
):
    """
    Test case: reject expired consultation booking token.

    What we verify:
    - Expired entitlement cannot access booking flow.
    - Service raises HTTP 403.
    """

    service_addon = ServiceAddon(
        code="consultation_1h_int_expired_test",
        name="1:1 SmartBudget consultation",
        service_type="consultation",
        usage_type="standalone",
        family_slug="smartbudget",
        package_code="INT",
        currency_code="EUR",
        amount=Decimal("79.00"),
        is_active=True,
    )
    db_session.add(service_addon)
    db_session.flush()

    sale = create_standalone_service_sale(
        db=db_session,
        service_addon_id=service_addon.id,
        service_name=service_addon.name,
        customer_email="customer@example.com",
        amount=service_addon.amount,
        currency=service_addon.currency_code,
    )
    db_session.flush()

    sale_item = sale.items[0]

    entitlement = create_consultation_entitlement(
        db=db_session,
        sale_item=sale_item,
    )

    entitlement.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        get_valid_consultation_entitlement_by_token(
            db=db_session,
            booking_token=entitlement.booking_token,
        )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "Consultation booking link has expired."
    )