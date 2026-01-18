from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.products_catalog import products_index
from fastapi import HTTPException
from app.products_catalog import product_by_slug

from .core.config import settings
from .core.logging import setup_logging
from .api.v1.routes import router as v1_router
from .core.i18n import get_lang, set_lang_cookie, t

def create_app() -> FastAPI:
    setup_logging()

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]
    if settings.APP_ENV == "dev" and not origins:
        origins = ["*"]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static & templates
    application.mount("/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")

    @application.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        lang = get_lang(request)
        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "lang": lang,
                "t": lambda k: t(lang, k),
                "app_name": settings.APP_NAME,
                "env": settings.APP_ENV,
            },
        )
        # If user explicitly changed language via ?lang=..., persist it
        if (request.query_params.get("lang") or "").lower() in {"en", "ru"}:
            set_lang_cookie(response, lang)
        return response

    @application.get("/products", response_class=HTMLResponse)
    async def products(request: Request):
        lang = get_lang(request)
        response = templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "lang": lang,
                "t": lambda k: t(lang, k),
                "products": products_index(),
            },
        )
        if (request.query_params.get("lang") or "").lower() in {"en", "ru"}:
            set_lang_cookie(response, lang)
        return response


    @application.get("/products/{slug}", response_class=HTMLResponse)
    async def product_detail(request: Request, slug: str):
        lang = get_lang(request)
        product = product_by_slug(slug)
        if not product:
            raise HTTPException(status_code=404)
        response = templates.TemplateResponse(
            "product_detail.html",
            {"request": request, "lang": lang, "t": lambda k: t(lang, k), "product": product},
        )
        if (request.query_params.get("lang") or "").lower() in {"en", "ru"}:
            set_lang_cookie(response, lang)
        return response


    # API v1
    application.include_router(v1_router)

    return application

app = create_app()


# *** *** ***
# uvicorn app.main:app --reload