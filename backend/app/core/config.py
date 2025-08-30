from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "SmartBudget API"
    APP_ENV: str = "dev"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    # Comma-separated list for dev, e.g. http://127.0.0.1:5173,http://localhost:5173
    BACKEND_CORS_ORIGINS: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
