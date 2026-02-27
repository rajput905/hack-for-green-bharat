"""
GreenFlow AI - Events Routes

CRUD and listing endpoints for environmental sensor events.
"""

from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Event
from app.database.session import get_db
from app.pipeline.extractor import compute_carbon_score, compute_risk_score
from app.schemas import EventCreate, EventResponse
from app.services.alerts import alert_service

router = APIRouter(prefix="/events", tags=["Events"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a new environmental event",
)
async def create_event(payload: EventCreate, db: DbDep) -> EventResponse:
    """
    Accept a raw CO2 sensor reading, enrich it with computed features,
    persist it to the database, and trigger automated alerts if needed.

    Args:
        payload: Validated event create schema.
        db:      Injected async database session.

    Returns:
        The saved event with computed risk and carbon scores.
    """
    event = Event(
        source=payload.source,
        timestamp=payload.timestamp or time.time(),
        co2_ppm=payload.co2_ppm,
        risk_score=compute_risk_score(payload.co2_ppm),
        carbon_score=compute_carbon_score(payload.co2_ppm),
        location=payload.location,
        raw_payload=payload.model_dump_json(),
    )
    db.add(event)
    await db.flush()  # get event.id before alert evaluation

    await alert_service.evaluate(event, db)
    await db.commit()
    await db.refresh(event)

    return EventResponse.model_validate(event)


@router.get(
    "",
    response_model=list[EventResponse],
    summary="List recent environmental events",
)
async def list_events(
    db: DbDep,
    limit: int = Query(50, ge=1, le=500, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> list[EventResponse]:
    """
    Return the most recent events ordered by timestamp descending.

    Args:
        db:     Injected async database session.
        limit:  Maximum records to return (1-500).
        offset: Pagination offset.

    Returns:
        Ordered list of event response objects.
    """
    result = await db.execute(
        select(Event)
        .order_by(Event.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    events = result.scalars().all()
    return [EventResponse.model_validate(e) for e in events]


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get a single event by ID",
)
async def get_event(event_id: int, db: DbDep) -> EventResponse:
    """
    Retrieve a specific event by its primary-key ID.

    Args:
        event_id: Integer primary key.
        db:       Injected async database session.

    Returns:
        Event response object.

    Raises:
        HTTPException 404: When no event with the given ID exists.
    """
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found.")
    return EventResponse.model_validate(event)
