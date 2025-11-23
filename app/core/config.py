from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Settings
    api_title: str = Field(default="Axiom API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    debug: bool = Field(default=False, description="Debug mode")

    # LLM Settings
    google_api_key: str = Field(..., description="Google API key for Gemini")
    llm_model: str = Field(default="gemini-3-pro-preview", description="LLM model name")

    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # CORS Settings
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")

    # Prompt File
    prompt_file_path: str = Field(
        default="app/prompts/system_prompt.md", description="Path to system prompt file"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
