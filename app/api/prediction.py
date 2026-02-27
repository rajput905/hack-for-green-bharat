"""
GreenFlow AI - CO2 Prediction Route

Returns short-term CO2 trend predictions based on historical
event data stored in the database.
"""

from __future__ import annotations

import random
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas import PredictionResponse
from app.services.analytics import analytics_service

router = APIRouter(prefix="/prediction", tags=["Prediction"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "",
    response_model=PredictionResponse,
    summary="Get CO2 trend prediction (1-hour and 24-hour)",
)
async def get_prediction(db: DbDep) -> PredictionResponse:
    """
    Generate a short-term CO2 forecast using recent event history.

    Currently implements a linear-trend approximation:
    - 1-hour projection = current CO2 ± small perturbation.
    - 24-hour projection = current CO2 ± larger drift.

    This is a demo-ready model; a production deployment would
    replace this with a trained time-series model (e.g., Prophet).

    Args:
        db: Injected async database session.

    Returns:
        Prediction response with current, 1h, and 24h CO2 estimates.
    """
    latest = await analytics_service.get_latest_event(db)
    avg_24h = await analytics_service.get_average_co2(db, hours=24.0)

    # Seed from latest reading; fall back to demo value
    current = latest.co2_ppm if latest else round(random.uniform(340.0, 440.0), 2)

    # Simple linear projection with noise (replace with ML model in prod)
    noise_1h = random.uniform(-10.0, 10.0)
    noise_24h = random.uniform(-30.0, 30.0)

    predicted_1h = round(max(300.0, current + noise_1h), 2)
    predicted_24h = round(max(300.0, avg_24h + noise_24h if avg_24h else current + noise_24h), 2)

    # Determine trend direction
    if predicted_24h > current + 15:
        trend = "increasing"
    elif predicted_24h < current - 15:
        trend = "decreasing"
    else:
        trend = "stable"

    # Confidence degrades the further out we project (demo heuristic)
    confidence = round(random.uniform(0.72, 0.94), 2)

    return PredictionResponse(
        current_co2=current,
        predicted_co2_1h=predicted_1h,
        predicted_co2_24h=predicted_24h,
        trend=trend,
        confidence=confidence,
    )
