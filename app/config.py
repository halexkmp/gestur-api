from typing import List, Literal
import os
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class Settings(BaseSettings):

    load_dotenv()
    # Environment
    ENVIRONMENT: Literal["development", "production"] = Field(
        default=os.getenv("ENVIRONMENT", "development")
    )
    DEBUG: bool = Field(default=False)

    # Security / Auth
    SECRET_KEY: str | None = Field(default=None)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str | None = Field(default=None)

    # Vercel Blob
    BLOB_STORE_ID: str | None = Field(default=os.getenv("BLOB_STORE_ID"))
    BLOB_READ_WRITE_TOKEN: str | None = Field(default=os.getenv("BLOB_READ_WRITE_TOKEN"))
    BLOB_FOLDER: str | None = Field(default=os.getenv("BLOB_FOLDER"))
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default_factory=list)

    # ORM / Migrations
    GENERATE_SCHEMAS: bool = Field(default=True)
    RUN_MIGRATIONS_ON_STARTUP: bool = Field(default=False)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _apply_env_defaults(self):  # type: ignore[override]
        is_production = self.ENVIRONMENT == "production"

        # DEBUG flag
        self.DEBUG = not is_production

        # Database URL defaults and validation
        if not self.DATABASE_URL:
            self.DATABASE_URL = os.getenv(
                "DATABASE_URL",
                "postgres://postgres:postgres@localhost:5432/gestur"
                if not is_production
                else None,
            )
        if is_production and not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL must be set in production environment"
            )

        # Secret key defaults and validation
        if not self.SECRET_KEY:
            self.SECRET_KEY = os.getenv(
                "SECRET_KEY",
                "dev-secret-key-change-me" if not is_production else None,
            )
        if is_production and not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set in production environment"
            )

        # Allowed origins parsing: comma-separated string in env
        self.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", ["*"])

        # Generate schemas only in development by default
        self.GENERATE_SCHEMAS = not is_production

        return self


settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.shared.db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
