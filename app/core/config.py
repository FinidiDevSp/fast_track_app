from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore any other stray env keys
    )


settings = Settings()
