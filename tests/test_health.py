"""
GreenFlow AI – Test Suite: Health Check

Verifies that the /api/v1/health endpoint is available and
returns the expected response format.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    """Health endpoint must return HTTP 200 with status=ok."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "components" in data


@pytest.mark.asyncio
async def test_risk_endpoint_returns_valid_schema() -> None:
    """Risk endpoint must return a valid risk assessment response."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/risk")

    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["risk_level"] in ("safe", "warning", "danger", "critical")


@pytest.mark.asyncio
async def test_prediction_endpoint() -> None:
    """Prediction endpoint must return current and forecast CO2 values."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/prediction")

    assert response.status_code == 200
    data = response.json()
    assert "current_co2" in data
    assert "predicted_co2_1h" in data
    assert "predicted_co2_24h" in data
    assert data["trend"] in ("increasing", "decreasing", "stable")


@pytest.mark.asyncio
async def test_recommendation_endpoint() -> None:
    """Recommendation endpoint must return a structured recommendation."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/recommendation")

    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "recommendation" in data
    assert isinstance(data["actions"], list)
    assert len(data["actions"]) > 0
    assert data["urgency"] in ("low", "medium", "high", "critical")


@pytest.mark.asyncio
async def test_events_list_empty() -> None:
    """Events list must return 200 with an empty list when no events exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/events")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_event() -> None:
    """POST /events must create and return an event with computed fields."""
    payload = {"source": "test-sensor", "co2_ppm": 420.5, "location": "Delhi"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/events", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["source"] == "test-sensor"
    assert data["co2_ppm"] == 420.5
    assert "risk_score" in data
    assert data["risk_score"] > 0
