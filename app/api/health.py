"""
GreenFlow AI - Health Check Route

Exposes GET /api/v1/health for load balancer and CI probes.
"""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.config import settings
from app.database.session import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    description="Returns service health status and component availability.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Health-check endpoint used by Docker, Kubernetes, and CI pipelines.

    Verifies database connectivity and returns component statuses.
    """
    components: dict = {}

    # Database ping
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = "ok"
    except Exception as exc:
        components["database"] = f"error: {exc}"

    # OpenAI presence (key configured, not validated)
    components["openai"] = "configured" if settings.OPENAI_API_KEY else "not configured"

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        components=components,
    )
