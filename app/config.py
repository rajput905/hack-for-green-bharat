"""
GreenFlow AI - Application Configuration

Manages all environment variables and settings using pydantic-settings.
Never hardcode secrets - always load from environment.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings loaded from environment variables or .env file.

    All sensitive values (API keys, secrets) must be set via environment variables.
    Non-sensitive values may have defaults for local development.
    """

    # ── OpenAI ──────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./greenflow.db"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"

    # ── App Metadata ─────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_NAME: str = "GreenFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ── Streaming / Pipeline ──────────────────────────────────────────────────
    PIPELINE_INPUT_DIR: str = "./data/input"
    PIPELINE_OUTPUT_FILE: str = "./data/output/enriched.jsonl"

    # ── Vector Store ─────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    RAG_COLLECTION_NAME: str = "greenflow_docs"

    # ── Thresholds ───────────────────────────────────────────────────────────
    CO2_DANGER_THRESHOLD: float = 400.0
    CO2_WARNING_THRESHOLD: float = 350.0
    RISK_SCORE_MAX: float = 1.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()


# Convenience alias used throughout the codebase
settings = get_settings()
