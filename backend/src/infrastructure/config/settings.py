"""Application settings."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database
    # IMPORTANT: Set DATABASE_URL environment variable. Do NOT hardcode credentials.
    # Example: DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
    # For development: DATABASE_URL=sqlite+aiosqlite:///./pastryjoy.db
    database_url: str

    # Security
    # IMPORTANT: Set SECRET_KEY environment variable. Generate with: openssl rand -hex 32
    # NEVER use default values in production!
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application
    debug: bool = False
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        """Parse allowed origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
