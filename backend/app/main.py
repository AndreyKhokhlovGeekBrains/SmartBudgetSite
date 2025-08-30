from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .core.config import settings
from .core.logging import setup_logging
from .api.v1.routes import router as v1_router

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
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "app_name": settings.APP_NAME, "env": settings.APP_ENV},
        )

    @application.get("/products", response_class=HTMLResponse)
    async def products(request: Request):
        return templates.TemplateResponse("products.html", {"request": request})

    # API v1
    application.include_router(v1_router)

    return application

app = create_app()


# *** *** ***
# uvicorn app.main:app --reload