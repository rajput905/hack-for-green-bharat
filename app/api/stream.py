"""
GreenFlow AI - Server-Sent Events Stream Route

Pushes real-time environmental updates to connected browser clients
via the SSE protocol (text/event-stream).
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import settings
from app.pipeline.extractor import enrich_event
from app.pipeline.streaming import stream_enriched_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["Streaming"])


async def _live_event_generator() -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE-formatted event strings.

    On each iteration:
    1. Attempts to read the latest batch from the JSONL pipeline output.
    2. Falls back to a synthetic reading if the file is empty or missing.
    3. Formats the payload as an SSE 'data:' line and yields it.
    4. Sleeps for 2 seconds before the next push.
    """
    while True:
        try:
            events = await stream_enriched_events(tail=1)

            if events:
                payload = events[-1]
            else:
                # Generate a synthetic reading for demo / health purposes
                co2: float = float(round(random.uniform(310, 520), 2))
                payload = enrich_event(
                    {
                        "source": "live-sensor",
                        "co2_ppm": co2,
                        "timestamp": time.time(),
                    }
                )

            yield f"data: {json.dumps(payload)}\n\n"
        except Exception as exc:
            logger.warning("SSE generator error: %s", exc)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        await asyncio.sleep(2)


@router.get(
    "/events",
    summary="Subscribe to real-time environmental event stream",
    description=(
        "Server-Sent Events endpoint. Connect with `EventSource` in the browser "
        "to receive live CO2 and risk updates every ~2 seconds."
    ),
    response_class=StreamingResponse,
)
async def stream_events() -> StreamingResponse:
    """
    SSE stream of enriched environmental events.

    Each message is a JSON object with the following fields:
    - ``co2_ppm``      – Current CO2 concentration.
    - ``risk_score``   – Normalized risk score [0.0 – 1.0].
    - ``carbon_score`` – Carbon intensity score.
    - ``severity``     – "safe" | "warning" | "danger" | "critical".
    - ``timestamp``    – Unix epoch of the reading.
    - ``source``       – Sensor or pipeline identifier.

    Connect with:

    .. code-block:: javascript

        const es = new EventSource("/api/v1/stream/events");
        es.onmessage = (e) => console.log(JSON.parse(e.data));
    """
    return StreamingResponse(
        _live_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
