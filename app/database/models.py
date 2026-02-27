"""
GreenFlow AI - ORM Models

Defines all SQLAlchemy table models for persistent storage.
"""

import time

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Event(Base):
    """
    Environmental sensor event captured from a data source.

    Each row represents one processed observation with an associated
    CO2 reading and computed risk score.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, default=time.time, index=True)
    co2_ppm: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbon_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Event id={self.id} source={self.source!r} "
            f"co2={self.co2_ppm} risk={self.risk_score:.2f}>"
        )


class SystemAlert(Base):
    """
    Triggered alert when a sensor event exceeds safe thresholds.
    """

    __tablename__ = "system_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="warning")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, default=time.time, index=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return (
            f"<SystemAlert id={self.id} type={self.alert_type!r} "
            f"severity={self.severity!r} resolved={self.resolved}>"
        )


class QueryLog(Base):
    """
    Audit log for all AI RAG queries made through the query endpoint.
    """

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=True)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[float] = mapped_column(Float, default=time.time, index=True)

    def __repr__(self) -> str:
        return f"<QueryLog id={self.id} query={self.query[:40]!r}>"
