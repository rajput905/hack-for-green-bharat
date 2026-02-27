"""
GreenFlow AI - Risk Assessment Route

Returns the current environmental risk score and severity classification
based on the latest sensor reading stored in the database.
"""

from __future__ import annotations

import random
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.session import get_db
from app.pipeline.extractor import classify_severity, compute_risk_score
from app.schemas import RiskResponse
from app.services.analytics import analytics_service

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "",
    response_model=RiskResponse,
    summary="Get current environmental risk assessment",
)
async def get_risk(db: DbDep) -> RiskResponse:
    """
    Compute and return the current environmental risk level.

    Uses the most recent event from the database if available;
    generates a synthetic sample as fallback for demo environments.

    Args:
        db: Injected async database session.

    Returns:
        Risk assessment response with score, level, and message.
    """
    latest = await analytics_service.get_latest_event(db)

    if latest:
        co2 = latest.co2_ppm
    else:
        # Demo fallback: simulate a mid-range reading
        co2: float = float(round(random.uniform(310.0, 480.0), 2))

    risk_score = compute_risk_score(co2)
    severity = classify_severity(co2)

    messages = {
        "safe": "✅ CO2 levels are within safe range. No action required.",
        "warning": "⚠️  CO2 is elevated. Consider improving ventilation.",
        "danger": "🔴 Dangerous CO2 level detected. Take immediate action.",
        "critical": "🚨 CRITICAL: CO2 is at hazardous levels. Evacuate if necessary.",
    }

    return RiskResponse(
        risk_score=risk_score,
        risk_level=severity,
        co2_ppm=co2,
        threshold=settings.CO2_DANGER_THRESHOLD,
        message=messages.get(severity, "Unknown risk level."),
    )
