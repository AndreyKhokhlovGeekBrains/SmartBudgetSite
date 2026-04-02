from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.products_catalog import products_index, product_by_slug
from app.core.i18n import get_lang, set_lang_cookie, t

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