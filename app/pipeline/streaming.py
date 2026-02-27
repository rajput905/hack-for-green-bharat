"""
GreenFlow AI - Streaming Pipeline

Simulates the real-time streaming pipeline that continuously reads
environmental sensor data, enriches it, and writes JSONL output.

In production this would integrate with Pathway, Apache Kafka,
or a similar streaming platform.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path

from app.config import settings
from app.pipeline.extractor import enrich_event

logger = logging.getLogger(__name__)


def _ensure_dirs() -> None:
    """Create pipeline input/output directories if they do not exist."""
    Path(settings.PIPELINE_INPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.PIPELINE_OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)


def process_file(filepath: str) -> list[dict]:
    """
    Read a JSON or JSONL file and enrich every event found.

    Args:
        filepath: Absolute or relative path to the sensor data file.

    Returns:
        List of enriched event dictionaries.
    """
    enriched: list[dict] = []
    try:
        with open(filepath, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                    enriched.append(enrich_event(raw))
                except json.JSONDecodeError as exc:
                    logger.warning("Skipping malformed line in %s: %s", filepath, exc)
    except FileNotFoundError:
        logger.error("Pipeline input file not found: %s", filepath)
    return enriched


def write_output(events: list[dict]) -> None:
    """
    Append enriched events to the JSONL output file.

    Args:
        events: Enriched event dictionaries to persist.
    """
    output_path = settings.PIPELINE_OUTPUT_FILE
    with open(output_path, "a", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event) + "\n")
    logger.info("Wrote %d enriched events to %s", len(events), output_path)


def run_pipeline() -> None:
    """
    Start the real-time streaming pipeline (synchronous entry point).

    Scans the input directory for new JSON files, processes each one,
    writes enriched output, and then removes the processed file.
    """
    _ensure_dirs()
    logger.info("Streaming pipeline started. Watching: %s", settings.PIPELINE_INPUT_DIR)
    input_dir = Path(settings.PIPELINE_INPUT_DIR)

    while True:
        for json_file in input_dir.glob("*.json"):
            logger.info("Processing pipeline file: %s", json_file)
            enriched = process_file(str(json_file))
            if enriched:
                write_output(enriched)
            try:
                os.remove(json_file)
            except OSError as exc:
                logger.warning("Could not remove processed file %s: %s", json_file, exc)
        time.sleep(2)


async def stream_enriched_events(tail: int = 50) -> list[dict]:
    """
    Read the last *tail* events from the JSONL output file.

    Used by the SSE endpoint to push recent data to connected clients.

    Args:
        tail: Maximum number of recent events to return.

    Returns:
        List of enriched event dictionaries (newest last).
    """
    await asyncio.sleep(0)  # yield to event loop
    output_path = Path(settings.PIPELINE_OUTPUT_FILE)
    if not output_path.exists():
        return []

    events: list[dict] = []
    try:
        with open(output_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except OSError:
        return []

    tail_events: list[dict] = events[-tail:]
    return tail_events
