"""
GreenFlow AI - Chatbot Service

Thin service layer that wraps the RAG engine with business logic,
including live CO2 context injection and query-log persistence.
"""

from __future__ import annotations

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import QueryLog
from app.rag.engine import rag_engine

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    High-level chatbot service used by the /query API route.

    Coordinates:
    - RAG engine call with live environmental context.
    - Persistence of query + answer to the QueryLog table.
    """

    async def get_answer(
        self,
        query: str,
        db: AsyncSession | None = None,
        live_co2: float | None = None,
    ) -> dict:
        """
        Get an AI-generated answer for an environmental question.

        Args:
            query:    User question string.
            db:       Optional async DB session used to persist the log entry.
            live_co2: Most recent CO2 reading to provide as live context.

        Returns:
            Dict with keys: ``answer``, ``sources``, ``latency_ms``.
        """
        result = await rag_engine.query(query, live_co2=live_co2)

        if db is not None:
            await self._log_query(db, query, result)

        return result

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    async def _log_query(db: AsyncSession, query: str, result: dict) -> None:
        """Persist the query and answer as an audit log entry."""
        try:
            log_entry = QueryLog(
                query=query,
                answer=result.get("answer", ""),
                source_count=len(result.get("sources", [])),
                latency_ms=result.get("latency_ms", 0.0),
                timestamp=time.time(),
            )
            db.add(log_entry)
            await db.flush()
        except Exception as exc:
            logger.warning("Failed to log query: %s", exc)


# ── Singleton ─────────────────────────────────────────────────────────────────
chatbot_service = ChatbotService()
