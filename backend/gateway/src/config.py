import os
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    PROJECT_TITLE: str = "E-Commerce app"
    PROJECT_DESCRIPTION: str = "E-Commerce app - bike shop"
    PROJECT_VERSION: str = "1.0"
    HOST_HTTP: str = "http://"
    HOST_URL: str = "localhost"
    HOST_PORT: int = 8000
    BASE_URL: str = f"{HOST_HTTP}{HOST_URL}:{HOST_PORT}"
    FRONTEND_BASE_URL: str = f"{HOST_HTTP}{HOST_URL}:3000"
    ALLOWED_ORIGINS: list[str] = os.environ.get('ALLOWED_ORIGINS', '*').split()

    BASE_DIR: Path = Path(__file__).resolve().parent
    GRPC_TOOLS_DIR: Path

    @validator('GRPC_TOOLS_DIR')
    def post_process_grpc_tools_dir(cls, value: str, values: dict[str, Any]):
        value = Path(value)
        if not value.is_absolute():
            return values['BASE_DIR'].parent / value
        return value


class DevelopmentSettings(Settings):
    ...


class ProductionSettings(Settings):
    ...


def get_settings() -> Settings:
    if os.environ.get('ENVIRONMENT', 'development').lower() == 'production':
        settings = ProductionSettings()
    else:
        settings = DevelopmentSettings()

    return settings


settings = get_settings()
