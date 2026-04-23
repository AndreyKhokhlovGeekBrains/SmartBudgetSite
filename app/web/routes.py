from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.products_catalog import products_index, product_by_slug
from app.core.i18n import get_lang, set_lang_cookie, t
from app.core.config import settings
from app.dependencies import get_db, require_admin
from app.repositories.feedback_admin_repository import FeedbackAdminRepository
from app.services.feedback_service import (
    send_feedback_reply,
    toggle_feedback_publish,
    toggle_feedback_resolved,
    save_feedback_reply_draft
    )
from app.models.product import ALLOWED_EDITIONS, ALLOWED_PRODUCT_STATUSES, Product
from app.models.product_price import ProductPrice

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import Product
from datetime import timezone, timedelta
from decimal import Decimal


moscow_tz = timezone(timedelta(hours=3))

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

ADMIN_COOKIE_NAME = "admin_token"

admin_router = APIRouter(
    dependencies=[Depends(require_admin)]
)


def render(request: Request, template_name: str, context: dict):
    lang = get_lang(request)

    response = templates.TemplateResponse(
        request,
        template_name,
        {
            "lang": lang,
            "t": lambda k: t(lang, k),
            **context,
        },
    )

    if (request.query_params.get("lang") or "").lower() in {"en", "ru"}:
        set_lang_cookie(response, lang)

    return response


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render(request, "index.html", {})


@router.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    return render(request, "products.html", {
        "products": products_index(),
    })


@router.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return render(request, "faq.html", {})


@router.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    return render(request, "feedback.html", {})


@router.get("/products/{slug}", response_class=HTMLResponse)
async def product_detail(request: Request, slug: str):
    product = product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404)

    template_name = "sm_landing.html" if slug == "smartbudget" else "product_detail.html"

    return render(request, template_name, {
        "product": product,
    })


@admin_router.get("/admin/feedback", response_class=HTMLResponse)
async def admin_feedback_list(
    request: Request,
    db: Session = Depends(get_db),
):
    repo = FeedbackAdminRepository(db)
    items = repo.list_feedback()

    return render(
        request,
        "admin_feedback_list.html",
        {
            "items": items,
        },
    )

@admin_router.get("/admin/feedback/{feedback_id}", response_class=HTMLResponse)
async def admin_feedback_detail(
    request: Request,
    feedback_id: int,
    db: Session = Depends(get_db),
):
    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404)

    local_reply_sent_at = None

    if item.reply_sent_at:
        local_reply_sent_at = item.reply_sent_at.astimezone(moscow_tz)

    return render(
        request,
        "admin_feedback_detail.html",
        {
            "item": item,
            "local_reply_sent_at": local_reply_sent_at,
        },
    )


@admin_router.post("/admin/feedback/{feedback_id}/resolve")
async def admin_feedback_resolve(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    toggle_feedback_resolved(db=db, feedback_id=feedback_id)

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}",
        status_code=303,
    )


@admin_router.post("/admin/feedback/{feedback_id}/reply")
async def admin_feedback_save_reply(
    feedback_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    admin_reply = str(form.get("admin_reply", ""))

    save_feedback_reply_draft(
        db=db,
        feedback_id=feedback_id,
        admin_reply=admin_reply,
    )

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}?saved=1",
        status_code=303,
    )


@admin_router.post("/admin/feedback/{feedback_id}/publish")
async def admin_feedback_toggle_publish(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    toggle_feedback_publish(db=db, feedback_id=feedback_id)

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}",
        status_code=303,
    )


@admin_router.post("/admin/feedback/{feedback_id}/send-email")
def send_feedback_email(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    try:
        send_feedback_reply(db=db, feedback_id=feedback_id)

        return RedirectResponse(
            url=f"/admin/feedback/{feedback_id}?email_sent=1",
            status_code=303,
        )

    except HTTPException as e:
        return RedirectResponse(
            url=f"/admin/feedback/{feedback_id}?error={e.detail}",
            status_code=303,
        )


@router.get("/reviews/{slug}", response_class=HTMLResponse)
async def reviews_page(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    feedback_repo = FeedbackAdminRepository(db)

    product = db.execute(
        select(Product).where(Product.slug == slug)
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404)

    reviews = feedback_repo.list_published_product_feedback(
        product_id=product.id
    )

    return render(request, "reviews.html", {
        "reviews": reviews,
        "product": product,
    })


@router.get("/reviews")
async def reviews_redirect():
    return RedirectResponse(url="/reviews/smartbudget", status_code=307)


@admin_router.get("/admin/products")
async def admin_products_list(
    request: Request,
    db: Session = Depends(get_db),
):
    from app.repositories.products_repository import ProductsRepository

    repo = ProductsRepository(db)
    product_list = repo.list_products()

    lang = get_lang(request)

    return templates.TemplateResponse(
        request,
        "admin_products_list.html",
        {
            "products": product_list,
            "t": lambda key: t(lang, key),
        },
    )


@admin_router.get("/admin/products/new")
async def admin_products_new(request: Request):
    return render(
        request,
        "admin_product_form.html",
        {
            "product": None,
            "active_price": None,
            "allowed_editions": sorted(ALLOWED_EDITIONS),
            "allowed_statuses": sorted(ALLOWED_PRODUCT_STATUSES),
            "form_action": "/admin/products/new",
            "page_title": "Create product",
        },
    )


@admin_router.post("/admin/products/new")
async def admin_products_create(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    slug: str = Form(...),
    edition: str = Form(...),
    version: str = Form(...),
    price: Decimal = Form(...),
    currency_code: str = Form(...),
    status: str = Form(...),
):
    """
    Creates product and its initial active price.

    Business rules:
    - Product is stored in Product table
    - Price is stored in ProductPrice table
    - New price is created as active
    - Currency code is normalized to uppercase

    Side effects:
    - Inserts one row into products
    - Inserts one row into product_prices

    Invariants / restrictions:
    - price must not be stored in Product model
    - currency_code is stored as uppercase ISO-like code
    """

    product = Product(
        name=name.strip(),
        slug=slug.strip(),
        edition=edition,
        version=version.strip(),
        status=status,
    )

    db.add(product)
    db.flush()

    product_price = ProductPrice(
        product_id=product.id,
        currency_code=currency_code.strip().upper(),
        amount=price,
        is_active=True,
    )

    db.add(product_price)
    db.commit()

    return RedirectResponse(
        url="/admin/products",
        status_code=303,
    )


@admin_router.get("/admin/products/{product_id}/edit")
async def admin_products_edit(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Opens edit form for existing product with active price.

    Business rules:
    - Product must exist
    - Active price is loaded separately from ProductPrice
    - Form must receive both product and current active price

    Side effects:
    - None

    Invariants / restrictions:
    - Returns 404 if product not found
    """

    from sqlalchemy import select
    from app.models.product_price import ProductPrice

    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404)

    active_price = db.execute(
        select(ProductPrice).where(
            ProductPrice.product_id == product_id,
            ProductPrice.is_active == True  # noqa: E712
        )
    ).scalar_one_or_none()

    lang = get_lang(request)

    return templates.TemplateResponse(
        request,
        "admin_product_form.html",
        {
            "t": lambda key: t(lang, key),
            "product": product,
            "active_price": active_price,
            "allowed_editions": sorted(ALLOWED_EDITIONS),
            "allowed_statuses": sorted(ALLOWED_PRODUCT_STATUSES),
            "form_action": f"/admin/products/{product_id}/edit",
            "page_title": "Edit product",
        },
    )


@admin_router.post("/admin/products/{product_id}/edit")
async def admin_products_update(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    slug: str = Form(...),
    edition: str = Form(...),
    version: str = Form(...),
    price: Decimal = Form(...),
    currency_code: str = Form(...),
    status: str = Form(...),
):
    """
    Updates product fields and replaces active price if needed.

    Business rules:
    - Product must exist
    - Product fields are stored in Product
    - Price is stored in ProductPrice
    - Only one active price per product/currency should remain active

    Side effects:
    - Updates Product row
    - May deactivate existing active ProductPrice row
    - May insert new active ProductPrice row

    Invariants / restrictions:
    - Returns 404 if product not found
    - currency_code is normalized to uppercase
    """

    from sqlalchemy import select
    from app.models.product_price import ProductPrice

    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404)

    product.name = name.strip()
    product.slug = slug.strip()
    product.edition = edition
    product.version = version.strip()
    product.status = status

    normalized_currency = currency_code.strip().upper()

    active_price = db.execute(
        select(ProductPrice).where(
            ProductPrice.product_id == product_id,
            ProductPrice.is_active == True,  # noqa: E712
        )
    ).scalar_one_or_none()

    should_replace_price = (
        active_price is None
        or active_price.amount != price
        or active_price.currency_code != normalized_currency
    )

    if should_replace_price:
        if active_price:
            active_price.is_active = False

        new_price = ProductPrice(
            product_id=product.id,
            currency_code=normalized_currency,
            amount=price,
            is_active=True,
        )
        db.add(new_price)

    db.commit()

    return RedirectResponse(
        url="/admin/products",
        status_code=303,
    )


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return render(request, "admin_login.html", {})


@router.post("/admin/login")
async def admin_login(
    request: Request,
    token: str = Form(...),
):
    """
    Stores admin token in cookie after successful validation.

    Business rules:
    - Login is allowed only when provided token matches settings.admin_token
    - Valid token is stored in cookie for subsequent admin requests

    Side effects:
    - Sets HTTP cookie in response

    Invariants / restrictions:
    - Invalid token returns 403
    """

    if token != settings.admin_token:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    response = RedirectResponse(
        url="/admin",
        status_code=303,
    )
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
    )
    return response


@admin_router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
):
    return render(
        request,
        "admin_dashboard.html",
        {}
    )


@admin_router.post("/admin/logout")
async def admin_logout():
    """
    Clears admin auth cookie and redirects to admin login page.

    Business rules:
    - Admin session is represented by cookie only
    - Logout must always clear the admin cookie

    Side effects:
    - Removes admin auth cookie from browser

    Invariants / restrictions:
    - Safe to call even if cookie is already missing
    """

    response = RedirectResponse(
        url="/admin/login",
        status_code=303,
    )
    response.delete_cookie("admin_token")
    return response


router.include_router(admin_router)