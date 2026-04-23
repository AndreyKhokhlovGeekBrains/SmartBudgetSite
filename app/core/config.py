import os
from pydantic_settings import BaseSettings, SettingsConfigDict


# ENV_FILE allows switching environments (dev/prod/test)
# Default is ".env" if ENV_FILE is not explicitly set
ENV_FILE = os.getenv("ENV_FILE", ".env")


class Settings(BaseSettings):
    APP_NAME: str = "SmartBudget API"
    APP_ENV: str = "dev"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    BACKEND_CORS_ORIGINS: str = ""
    DATABASE_URL: str = ""

    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    SECRET_KEY: str = ""
    UPLOAD_DIR: str = "uploads"

    MAIL_FROM_EMAIL: str = ""
    MAIL_FROM_NAME: str = "SmartBudget"
    MAIL_SMTP_HOST: str = ""
    MAIL_SMTP_PORT: int = 587
    MAIL_SMTP_USER: str = ""
    MAIL_SMTP_PASSWORD: str = ""
    MAIL_SMTP_TLS: bool = True

    admin_token: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="forbid",
    )


settings = Settings()