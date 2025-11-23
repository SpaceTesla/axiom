from fastapi import Depends

from app.core.config import Settings
from app.core.dependencies import get_settings


def get_config(settings: Settings = Depends(get_settings)) -> Settings:
    """Dependency to get application configuration."""
    return settings

