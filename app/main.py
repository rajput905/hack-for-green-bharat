"""
GreenFlow AI - FastAPI Application Entry Point

This module bootstraps the FastAPI application, registers all routers,
configures CORS and static file serving, and manages the application
lifecycle (database init, RAG seeding, pipeline launch).

Run with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import events, health, prediction, query, recommendation, risk, stream
from app.config import settings
from app.database.session import init_db
from app.pipeline.streaming import run_pipeline
from app.rag.engine import rag_engine

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Startup:
    - Creates all database tables.
    - Seeds the RAG knowledge base.
    - Launches the streaming pipeline in a background daemon thread.

    Shutdown:
    - Graceful teardown (connections auto-closed by SQLAlchemy).
    """
    logger.info("🌱 GreenFlow AI starting up …")

    # Database
    await init_db()
    logger.info("✅ Database tables ready.")

    # RAG knowledge base
    try:
        rag_engine.seed_knowledge_base()
    except Exception as exc:
        logger.warning("RAG seeding failed: %s", exc)

    # Start streaming pipeline in background thread (non-blocking)
    pipeline_thread = threading.Thread(target=run_pipeline, daemon=True, name="pipeline")
    pipeline_thread.start()
    logger.info("✅ Streaming pipeline started (daemon thread).")

    logger.info("🚀 GreenFlow AI is live at http://0.0.0.0:%s", 8000)
    yield

    logger.info("🛑 GreenFlow AI shutting down …")


# ── App factory ───────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns:
        Fully configured FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Real-time environmental AI monitoring system powering the "
            "'Hack for Green Bharat' initiative. Provides CO2 tracking, "
            "risk scoring, AI recommendations, and live streaming insights."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── API Routers ───────────────────────────────────────────────────────────
    API_PREFIX = "/api/v1"

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(events.router, prefix=API_PREFIX)
    app.include_router(query.router, prefix=API_PREFIX)
    app.include_router(stream.router, prefix=API_PREFIX)
    app.include_router(risk.router, prefix=API_PREFIX)
    app.include_router(prediction.router, prefix=API_PREFIX)
    app.include_router(recommendation.router, prefix=API_PREFIX)

    # ── Static Frontend ───────────────────────────────────────────────────────
    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

    return app


app = create_app()
