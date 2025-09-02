import os

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> str:
    # Highest priority: explicit path via ENV_FILE
    explicit = os.getenv("ENV_FILE")
    if explicit and explicit.strip():
        return explicit.strip()

    # Next: environment name via APP_ENV/ENV/ENVIRONMENT
    env_name = (
        os.getenv("APP_ENV") or os.getenv("ENV") or os.getenv("ENVIRONMENT") or "develop"
    ).lower()

    mapping = {
        "dev": ".env.develop",
        "develop": ".env.develop",
        "development": ".env.develop",
        "staging": ".env.staging",
        "stage": ".env.staging",
        "prod": ".env.production",
        "production": ".env.production",
    }
    return mapping.get(env_name, ".env.develop")


class Settings(BaseSettings):
    PROJECT_NAME: str = "TrackMind API"
    API_V1_PREFIX: str = "/api/v1"
    # Accept both BACKEND_CORS_ORIGINS and legacy CORS_ORIGINS from env
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173"],
        validation_alias=AliasChoices("BACKEND_CORS_ORIGINS", "CORS_ORIGINS"),
    )
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    # Include SECRET_KEY so it's not treated as extra
    SECRET_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=_resolve_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",  # ignore any other stray env keys
    )


settings = Settings()
