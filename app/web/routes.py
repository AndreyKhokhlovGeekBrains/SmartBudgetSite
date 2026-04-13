from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.products_catalog import products_index, product_by_slug
from app.core.i18n import get_lang, set_lang_cookie, t
from app.dependencies import get_db
from app.repositories.feedback_admin_repository import FeedbackAdminRepository
from app.services.feedback_service import (
    send_feedback_reply,
    toggle_feedback_publish,
    toggle_feedback_resolved,
    save_feedback_reply_draft
    )
from app.models.product import ALLOWED_EDITIONS, ALLOWED_PRODUCT_STATUSES

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import Product
from datetime import timezone, timedelta

moscow_tz = timezone(timedelta(hours=3))

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


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


@router.get("/admin/feedback", response_class=HTMLResponse)
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

@router.get("/admin/feedback/{feedback_id}", response_class=HTMLResponse)
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


@router.post("/admin/feedback/{feedback_id}/resolve")
async def admin_feedback_resolve(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    toggle_feedback_resolved(db=db, feedback_id=feedback_id)

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}",
        status_code=303,
    )


@router.post("/admin/feedback/{feedback_id}/reply")
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


@router.post("/admin/feedback/{feedback_id}/publish")
async def admin_feedback_toggle_publish(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    toggle_feedback_publish(db=db, feedback_id=feedback_id)

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}",
        status_code=303,
    )


@router.post("/admin/feedback/{feedback_id}/send-email")
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


@router.get("/admin/products")
async def admin_products_list(request: Request, db: Session = Depends(get_db)):
    from app.repositories.products_repository import ProductsRepository

    repo = ProductsRepository(db)
    product_list  = repo.list_products()

    lang = get_lang(request)

    return templates.TemplateResponse(
        request,
        "admin_products_list.html",
        {
            "products": product_list,
            "t": lambda key: t(lang, key),
        },
    )


@router.get("/admin/products/new")
async def admin_products_new(request: Request):
    lang = get_lang(request)

    return templates.TemplateResponse(
        request,
        "admin_product_form.html",
        {
            "t": lambda key: t(lang, key),
            "product": None,
            "allowed_editions": sorted(ALLOWED_EDITIONS),
            "allowed_statuses": sorted(ALLOWED_PRODUCT_STATUSES),
            "form_action": "/admin/products/new",
            "page_title": "Create product",
        },
    )


from fastapi import Form

@router.post("/admin/products/new")
async def admin_products_create(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    slug: str = Form(...),
    edition: str = Form(...),
    version: str = Form(...),
    price: float = Form(...),
    status: str = Form(...),
):
    from app.models.product import Product

    product = Product(
        name=name,
        slug=slug,
        edition=edition,
        version=version,
        price=price,
        status=status,
    )

    db.add(product)
    db.commit()

    return RedirectResponse(
        url="/admin/products",
        status_code=303,
    )