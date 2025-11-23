from functools import lru_cache

from app.core.config import Settings


@lru_cache()
def get_settings() -> Settings:
    """Dependency to get application settings."""
    return Settings()

