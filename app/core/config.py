from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variables"""

    # App
    PROJECT_NAME: str = "Oh My Match Backend"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Professional FastAPI template"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Development - Disable auth for testing (Postman, etc.)
    DISABLE_AUTH: bool = False  # Set to True to bypass JWT verification

    # Better Auth
    BETTER_AUTH_URL: str = ""  # URL of your Next.js Better Auth API (e.g., http://localhost:3000)
    BETTER_AUTH_SECRET: str = ""  # Better Auth secret for server-side verification

    # AI
    GEMINI_API_KEY: str = ""
    FIT_BUDDY_DATA_URL: str = "http://localhost:8001"


    BACKEND_CORS_ORIGINS: Any = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            # Strip quotes that might come from .env file
            v = v.strip('"').strip("'")
            # Handle "*" for all origins
            if v == "*":
                return ["*"]
            # Handle comma-separated list
            if not v.startswith("["):
                return [i.strip() for i in v.split(",")]
        if isinstance(v, list):
            return v
        raise ValueError(v)

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Database (PostgreSQL)
    DATABASE_URL: str = ""
    MIGRATION_URL: str = ""  # Specific URL for Alembic (e.g. Direct Connection / Transaction Mode)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fallback_database_url(cls, v: Any, info: Any) -> Any:
        # If DATABASE_URL is not set, we can't easily access MIGRATION_URL in field_validator mode='before'
        # if the fields are not yet validated.
        # So we'll accept empty string here and handle it in a model validator.
        return v
    
    def model_post_init(self, __context: Any) -> None:
        if (not self.DATABASE_URL or self.DATABASE_URL == "test") and self.MIGRATION_URL:
            self.DATABASE_URL = self.MIGRATION_URL
        super().model_post_init(__context)

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
