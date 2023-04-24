from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
