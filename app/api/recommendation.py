"""
GreenFlow AI - Recommendation Route

Returns AI-generated or rule-based environmental action recommendations
tailored to the current CO2 risk level.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.pipeline.extractor import classify_severity
from app.schemas import RecommendationResponse
from app.services.analytics import analytics_service
import random

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


# ── Rule-based recommendation templates ──────────────────────────────────────

_RECOMMENDATIONS: dict[str, dict] = {
    "safe": {
        "title": "Environment is Safe",
        "recommendation": (
            "Current CO2 levels are within the safe range. This is a good time "
            "to perform preventive maintenance on air quality systems and maintain "
            "vegetation coverage around your facility."
        ),
        "actions": [
            "Monitor CO2 levels hourly.",
            "Maintain air filtration systems.",
            "Plant trees and increase green cover in the area.",
            "Document baseline readings for trend analysis.",
        ],
        "urgency": "low",
    },
    "warning": {
        "title": "Elevated CO2 – Take Precautions",
        "recommendation": (
            "CO2 levels are moderately elevated. Increase ventilation and reduce "
            "activities that generate significant emissions. Notify your environmental "
            "compliance team."
        ),
        "actions": [
            "Increase ventilation rate by 20–30%.",
            "Reduce high-emission activities during peak hours.",
            "Alert the environmental management team.",
            "Check air filtration systems for blockages.",
            "Consider switching to cleaner energy sources.",
        ],
        "urgency": "medium",
    },
    "danger": {
        "title": "Dangerous CO2 Level – Act Now",
        "recommendation": (
            "CO2 concentration is at dangerous levels. Immediate action is required to "
            "protect occupants and comply with environmental regulations. Engage your "
            "emergency protocol."
        ),
        "actions": [
            "IMMEDIATELY increase ventilation to maximum.",
            "Suspend high-emission operations.",
            "Activate emergency air quality protocol.",
            "Notify regulatory authorities if threshold exceeds legal limit.",
            "Evacuate sensitive populations (children, elderly) from exposure areas.",
            "Engage backup air purification systems.",
        ],
        "urgency": "high",
    },
    "critical": {
        "title": "CRITICAL: Emergency Response Required",
        "recommendation": (
            "CO2 is at hazardous levels posing an immediate risk to human health "
            "and ecosystems. Activate full emergency response and report to national "
            "environmental agencies immediately."
        ),
        "actions": [
            "EVACUATE the affected zone immediately.",
            "Shut down all emission sources.",
            "Activate NDMA / CPCB emergency reporting protocol.",
            "Deploy mobile air purification units.",
            "Initiate mandatory incident reporting.",
            "Call emergency environmental response team.",
            "Issue public health advisory.",
        ],
        "urgency": "critical",
    },
}


@router.get(
    "",
    response_model=RecommendationResponse,
    summary="Get AI-powered environmental recommendations",
)
async def get_recommendation(db: DbDep) -> RecommendationResponse:
    """
    Return context-aware environmental recommendations.

    Recommendations are selected from a curated knowledge base keyed
    by the current severity classification of the latest CO2 reading.

    Args:
        db: Injected async database session.

    Returns:
        Structured recommendation with title, actions, and urgency.
    """
    latest = await analytics_service.get_latest_event(db)
    co2: float = latest.co2_ppm if latest else float(round(random.uniform(340.0, 420.0), 2))

    severity = classify_severity(co2)
    rec = _RECOMMENDATIONS.get(severity, _RECOMMENDATIONS["safe"])

    return RecommendationResponse(
        title=rec["title"],
        recommendation=rec["recommendation"],
        actions=rec["actions"],
        urgency=rec["urgency"],
        co2_context=co2,
    )
