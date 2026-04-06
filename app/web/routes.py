from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.products_catalog import products_index, product_by_slug
from app.core.i18n import get_lang, set_lang_cookie, t
from app.core.db import get_db
from app.repositories.feedback_admin_repository import FeedbackAdminRepository

from sqlalchemy.orm import Session

from datetime import datetime, UTC


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template_name: str, context: dict):
    lang = get_lang(request)

    response = templates.TemplateResponse(
        template_name,
        {
            "request": request,
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

    return render(
        request,
        "admin_feedback_detail.html",
        {
            "item": item,
        },
    )

@router.post("/admin/feedback/{feedback_id}/resolve")
async def admin_feedback_resolve(
    feedback_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404)

    repo.update_resolved_status(
        feedback_id=feedback_id,
        is_resolved=not item.is_resolved,
    )

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
    admin_reply = str(form.get("admin_reply", "")).strip()

    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404)

    item.admin_reply = admin_reply or None
    db.commit()

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}?saved=1",
        status_code=303,
    )

@router.post("/admin/feedback/{feedback_id}/publish")
async def admin_feedback_toggle_publish(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404)

    if item.type != "product_feedback":
        raise HTTPException(
            status_code=400,
            detail="Only product feedback can be published",
        )

    if not item.admin_reply:
        raise HTTPException(
            status_code=400,
            detail="Cannot publish without admin reply",
        )

    item.is_published = not item.is_published
    item.published_at = datetime.now(UTC) if item.is_published else None
    db.commit()

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}",
        status_code=303,
    )

@router.post("/admin/feedback/{feedback_id}/send-email")
def send_feedback_email(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # Only for non-public types (email communication)
    if item.type not in ("general_question", "site_issue"):
        raise HTTPException(
            status_code=400,
            detail="Email reply is not applicable for this feedback type",
        )

    if not item.admin_reply:
        raise HTTPException(
            status_code=400,
            detail="Cannot send email without reply text",
        )

    if item.reply_sent_at:
        raise HTTPException(
            status_code=400,
            detail="Email already sent",
        )

    if item.is_published:
        raise HTTPException(
            status_code=400,
            detail="Cannot send email for published review",
        )

    # Simulate sending email (later we replace with real SMTP)
    item.reply_sent_at = datetime.now(UTC)
    item.reply_sent_to_email = item.email

    db.commit()

    return RedirectResponse(
        url=f"/admin/feedback/{feedback_id}?email_sent=1",
        status_code=303,
    )