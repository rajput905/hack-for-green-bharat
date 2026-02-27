"""
GreenFlow AI – Application Configuration
=========================================

Single source of truth for all runtime settings.

All values are loaded from environment variables (or a ``.env`` file at the
project root).  **Never hard-code secrets or thresholds** in application code;
always reference ``settings.<VARIABLE>`` so they can be changed without
touching source code.

Usage
-----
::

    from app.config import settings

    if settings.is_production:
        ...
"""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application-wide settings loaded from environment variables or ``.env``.

    Attribute docstrings below are rendered in the auto-generated API docs and
    are also used by the ``/config/thresholds`` endpoint to self-document the
    current runtime configuration.
    """

    # ── OpenAI ──────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for the RAG engine.  Required for AI Q&A.",
    )

    # ── Database ────────────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./greenflow.db",
        description=(
            "SQLAlchemy async database URL. "
            "Use sqlite+aiosqlite for dev, postgresql+asyncpg for prod."
        ),
    )

    # ── Security ────────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Secret key used for internal signing / HMAC.  Must be changed in production.",
    )

    # ── Application Mode ────────────────────────────────────────────────────────
    APP_ENV: str = Field(
        default="development",
        description=(
            "Runtime environment.  "
            "``development`` enables /docs, DEBUG logging, and relaxed CORS.  "
            "``production`` disables /docs and /redoc, uses INFO logging."
        ),
    )
    APP_NAME: str = Field(default="GreenFlow AI", description="Human-readable application name.")
    APP_VERSION: str = Field(default="1.0.0", description="Semantic version string.")

    DEBUG: bool = Field(
        default=False,
        description=(
            "Enable verbose DEBUG-level logging.  "
            "Should always be ``false`` in production deployments."
        ),
    )

    # ── CORS ────────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = Field(
        default=["*"],
        description=(
            "List of allowed CORS origins.  "
            "Use ``[\"*\"]`` for development only; restrict to your domain in production."
        ),
    )

    # ── Streaming / Pipeline ────────────────────────────────────────────────────
    PIPELINE_INPUT_DIR: str = Field(
        default="./data/input",
        description="Directory the streaming pipeline watches for incoming JSONL sensor files.",
    )
    PIPELINE_OUTPUT_FILE: str = Field(
        default="./data/output/enriched.jsonl",
        description="Output file path for enriched event records produced by the pipeline.",
    )

    # ── Vector Store (ChromaDB) ─────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = Field(
        default="./data/chroma",
        description=(
            "Filesystem path where ChromaDB persists its vector index. "
            "Created automatically at startup if it does not exist. "
            "Use an absolute path in production."
        ),
    )
    RAG_COLLECTION_NAME: str = Field(
        default="greenflow_docs",
        description="Name of the ChromaDB collection used to store environmental documents.",
    )

    # ── CO₂ Thresholds ──────────────────────────────────────────────────────────
    CO2_WARNING_THRESHOLD: float = Field(
        default=350.0,
        description=(
            "CO₂ level (ppm) at which severity transitions from ``safe`` to ``warning``. "
            "CPCB guideline: 350 ppm."
        ),
    )
    CO2_DANGER_THRESHOLD: float = Field(
        default=400.0,
        description=(
            "CO₂ level (ppm) at which severity transitions from ``warning`` to ``danger`` "
            "and the alert engine is triggered.  Regulatory limit: 400 ppm."
        ),
    )
    CO2_CRITICAL_THRESHOLD: float = Field(
        default=500.0,
        description=(
            "CO₂ level (ppm) at which severity is classified as ``critical``. "
            "Above this level evacuation protocols should be considered."
        ),
    )
    RISK_SCORE_MAX: float = Field(
        default=1.0,
        description="Maximum capped value for the normalized risk score (0.0 – 1.0).",
    )

    # ── Pydantic v2 config ──────────────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",            # silently ignore any extra env vars
    )

    # ── Derived helpers ─────────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        """Return ``True`` when running in production mode."""
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Return ``True`` when running in development mode."""
        return not self.is_production

    @property
    def docs_url(self) -> str | None:
        """Return the Swagger UI URL, or ``None`` in production."""
        return None if self.is_production else "/docs"

    @property
    def redoc_url(self) -> str | None:
        """Return the ReDoc URL, or ``None`` in production."""
        return None if self.is_production else "/redoc"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton (thread-safe)."""
    return Settings()


# ---------------------------------------------------------------------------
# Convenience alias used throughout the codebase:
#   from app.config import settings
# ---------------------------------------------------------------------------
settings = get_settings()
