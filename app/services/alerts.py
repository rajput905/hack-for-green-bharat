"""
GreenFlow AI - Alert Service

Evaluates environmental readings and creates SystemAlert records
when CO2 levels or risk scores exceed configured thresholds.
"""

from __future__ import annotations

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import Event, SystemAlert
from app.pipeline.extractor import classify_severity

logger = logging.getLogger(__name__)


class AlertService:
    """
    Evaluates each ingested Event and triggers alerts as needed.
    """

    async def evaluate(self, event: Event, db: AsyncSession) -> list[SystemAlert]:
        """
        Inspect an event and emit any applicable alerts.

        Args:
            event: The newly persisted Event object.
            db:    Async database session used to persist alerts.

        Returns:
            List of SystemAlert objects created (may be empty).
        """
        created: list[SystemAlert] = []
        severity = classify_severity(event.co2_ppm)

        if severity in ("danger", "critical"):
            alert = SystemAlert(
                event_id=event.id,
                alert_type="HIGH_CO2",
                severity="critical" if severity == "critical" else "warning",
                message=(
                    f"CO2 level at {event.co2_ppm:.1f} ppm from '{event.source}' "
                    f"exceeds safe threshold ({settings.CO2_DANGER_THRESHOLD} ppm). "
                    f"Risk score: {event.risk_score:.2f}."
                ),
                timestamp=time.time(),
                resolved=False,
            )
            db.add(alert)
            created.append(alert)
            logger.warning(
                "ALERT triggered: HIGH_CO2 | source=%s co2=%.1f risk=%.2f",
                event.source,
                event.co2_ppm,
                event.risk_score,
            )

        if event.risk_score >= 0.9:
            alert = SystemAlert(
                event_id=event.id,
                alert_type="CRITICAL_RISK",
                severity="critical",
                message=(
                    f"Risk score {event.risk_score:.2f} from '{event.source}' is critically high. "
                    "Immediate action required."
                ),
                timestamp=time.time(),
                resolved=False,
            )
            db.add(alert)
            created.append(alert)
            logger.critical(
                "CRITICAL_RISK alert | source=%s risk=%.2f",
                event.source,
                event.risk_score,
            )

        if created:
            await db.flush()

        return created


# ── Singleton ─────────────────────────────────────────────────────────────────
alert_service = AlertService()
