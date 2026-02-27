"""
GreenFlow AI - Pydantic Request/Response Schemas

All API input/output types are defined here.
Using Pydantic v2 model syntax.
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
#  Events
# ═══════════════════════════════════════════════════════════════════════════════


class EventCreate(BaseModel):
    """Payload accepted by POST /api/v1/events."""

    source: str = Field(..., description="Sensor or data source identifier", examples=["sensor-01"])
    co2_ppm: float = Field(..., ge=0, description="CO2 concentration in parts per million")
    location: str | None = Field(None, description="Geographic location label")
    timestamp: float = Field(default_factory=time.time, description="Unix epoch timestamp")

    @field_validator("co2_ppm")
    @classmethod
    def co2_must_be_positive(cls, v: float) -> float:
        """Reject negative CO2 readings."""
        if v < 0:
            raise ValueError("co2_ppm must be non-negative")
        return v


class EventResponse(BaseModel):
    """Event data returned from GET or POST /api/v1/events."""

    id: int
    source: str
    timestamp: float
    co2_ppm: float
    risk_score: float
    carbon_score: float | None = None
    location: str | None = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
#  RAG / AI Query
# ═══════════════════════════════════════════════════════════════════════════════


class QueryRequest(BaseModel):
    """Payload accepted by POST /api/v1/query."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural-language environmental question",
        examples=["What is the current CO2 risk level?"],
    )


class QueryResponse(BaseModel):
    """Response returned by POST /api/v1/query."""

    answer: str
    sources: list[str] = Field(default_factory=list)
    latency_ms: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  Risk / Prediction
# ═══════════════════════════════════════════════════════════════════════════════


class RiskResponse(BaseModel):
    """Environmental risk assessment response."""

    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    co2_ppm: float
    threshold: float
    message: str


class PredictionResponse(BaseModel):
    """CO2 trend prediction response."""

    current_co2: float
    predicted_co2_1h: float
    predicted_co2_24h: float
    trend: str
    confidence: float


# ═══════════════════════════════════════════════════════════════════════════════
#  Recommendation
# ═══════════════════════════════════════════════════════════════════════════════


class RecommendationResponse(BaseModel):
    """AI-generated environmental recommendation."""

    title: str
    recommendation: str
    actions: list[str]
    urgency: str
    co2_context: float


# ═══════════════════════════════════════════════════════════════════════════════
#  Health Check
# ═══════════════════════════════════════════════════════════════════════════════


class HealthResponse(BaseModel):
    """Application health-check response."""

    status: str
    version: str
    environment: str
    components: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
#  Alerts
# ═══════════════════════════════════════════════════════════════════════════════


class AlertResponse(BaseModel):
    """System alert data."""

    id: int
    alert_type: str
    severity: str
    message: str
    timestamp: float
    resolved: bool

    model_config = {"from_attributes": True}
