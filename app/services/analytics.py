"""
GreenFlow AI - Analytics Service

Provides aggregation and statistical summaries over stored Event data.
Used by the analytics API routes to power the dashboard charts.
"""

from __future__ import annotations

import time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Event


class AnalyticsService:
    """
    Compute statistics and trend data from the events table.
    """

    @staticmethod
    async def get_latest_event(db: AsyncSession) -> Event | None:
        """
        Retrieve the most recent environmental event.

        Args:
            db: Async database session.

        Returns:
            Most recent Event object, or None if the table is empty.
        """
        result = await db.execute(
            select(Event).order_by(Event.timestamp.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_average_co2(db: AsyncSession, hours: float = 24.0) -> float:
        """
        Compute the average CO2 reading over the past *hours* hours.

        Args:
            db:    Async database session.
            hours: Time window in hours.

        Returns:
            Average CO2 in ppm, or 0.0 if no data.
        """
        since = time.time() - (hours * 3600)
        result = await db.execute(
            select(func.avg(Event.co2_ppm)).where(Event.timestamp >= since)
        )
        avg = result.scalar()
        return float(avg) if avg is not None else 0.0

    @staticmethod
    async def get_max_risk(db: AsyncSession, hours: float = 24.0) -> float:
        """
        Return the highest risk score recorded in the past *hours* hours.

        Args:
            db:    Async database session.
            hours: Time window in hours.

        Returns:
            Maximum risk score, or 0.0 if no data.
        """
        since = time.time() - (hours * 3600)
        result = await db.execute(
            select(func.max(Event.risk_score)).where(Event.timestamp >= since)
        )
        mx = result.scalar()
        return float(mx) if mx is not None else 0.0

    @staticmethod
    async def get_event_count(db: AsyncSession) -> int:
        """Return total number of events in the database."""
        result = await db.execute(select(func.count(Event.id)))
        return result.scalar() or 0


# ── Singleton ─────────────────────────────────────────────────────────────────
analytics_service = AnalyticsService()
