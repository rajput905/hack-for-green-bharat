"""
GreenFlow AI - RAG Engine

Implements Retrieval-Augmented Generation using ChromaDB for vector
storage and OpenAI for natural-language completions.

Flow:
  User Query → Vector Search (ChromaDB) → Context Merge → OpenAI → Answer
"""

from __future__ import annotations

import logging
import time
import typing
from pathlib import Path
from app.config import settings

if typing.TYPE_CHECKING:
    import chromadb
    from chromadb.api import Collection
    from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for environmental queries.

    Maintains a ChromaDB collection of environmental knowledge documents.
    On each query, retrieves the most relevant passages, merges them with
    the live CO2 context, and forwards to OpenAI for a grounded answer.
    """

    def __init__(self) -> None:
        self._client: typing.Any = None
        self._collection: typing.Any = None
        self._openai_client: typing.Any = None
        self._initialized = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def _init_clients(self) -> None:
        """Lazily initialize ChromaDB and OpenAI clients."""
        if self._initialized:
            return

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            persist_dir = settings.CHROMA_PERSIST_DIR
            Path(persist_dir).mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=settings.RAG_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            logger.warning("ChromaDB unavailable (%s). RAG will run without vector search.", exc)

        try:
            from openai import AsyncOpenAI

            self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as exc:
            logger.warning("OpenAI client unavailable: %s", exc)

        self._initialized = True

    # ── Document Indexing ─────────────────────────────────────────────────────

    def index_document(self, doc_id: str, text: str, metadata: dict | None = None) -> None:
        """
        Add or update a document in the vector store.

        Args:
            doc_id:   Unique identifier for the document.
            text:     Raw text content to embed and index.
            metadata: Optional key/value metadata attached to the document.
        """
        self._init_clients()
        if self._collection is None:
            logger.warning("ChromaDB not available – skipping index_document(%s)", doc_id)
            return

        # ChromaDB requires non-empty metadata – always include at least one key
        safe_meta = metadata if metadata else {"source": doc_id}
        
        # Defensive check for linter
        if self._collection is not None:
            self._collection.upsert(
                ids=[doc_id],
                documents=[text],
                metadatas=[safe_meta],
            )
        else:
            logger.warning("Attempted to index document %s, but collection is None", doc_id)
        logger.info("Indexed document '%s' into RAG collection.", doc_id)

    def seed_knowledge_base(self) -> None:
        """
        Seed the vector store with built-in environmental knowledge.

        Called once on application startup to ensure the collection
        contains baseline domain knowledge even before any user uploads.
        """
        knowledge = [
            {
                "id": "co2-basics",
                "text": (
                    "Carbon dioxide (CO2) is a greenhouse gas. Safe indoor levels are below "
                    "1000 ppm. Outdoor baseline is ~420 ppm. Levels above 1000 ppm cause "
                    "cognitive impairment; above 5000 ppm is immediately dangerous."
                ),
            },
            {
                "id": "risk-scoring",
                "text": (
                    "GreenFlow AI computes a risk score as min(co2_ppm / 500, 1.0). "
                    "A score of 0.0 is safe; 1.0 is critical. Scores above 0.8 trigger "
                    "automated alerts and recommend immediate ventilation and activity reduction."
                ),
            },
            {
                "id": "climate-impact",
                "text": (
                    "India emits approximately 2.88 billion tonnes of CO2 per year (~7% of "
                    "global emissions). Industrial zones, traffic corridors, and agricultural "
                    "burning are primary sources. Real-time monitoring helps target interventions."
                ),
            },
            {
                "id": "green-actions",
                "text": (
                    "Effective carbon-reduction actions include switching to renewable energy, "
                    "improving public transportation, reforestation, and circular manufacturing. "
                    "Each 1% reduction in industrial CO2 prevents ~2.5 MT of annual emissions."
                ),
            },
            {
                "id": "greenflow-system",
                "text": (
                    "GreenFlow AI is a real-time environmental monitoring system developed for "
                    "'Hack for Green Bharat'. It ingests sensor data, computes risk scores, "
                    "and serves AI-powered recommendations via FastAPI, SSE, and a browser dashboard."
                ),
            },
        ]
        for item in knowledge:
            self.index_document(item["id"], item["text"])
        logger.info("RAG knowledge base seeded with %d documents.", len(knowledge))

    # ── Query ─────────────────────────────────────────────────────────────────

    async def query(self, query: str, live_co2: float | None = None) -> dict:
        """
        Answer an environmental question using RAG.

        1. Retrieve relevant passages from ChromaDB.
        2. Merge retrieved context with the live CO2 snapshot.
        3. Send an enriched prompt to OpenAI.
        4. Return the structured answer with source references.

        Args:
            query:    Natural-language question from the user.
            live_co2: Most recent CO2 reading to inject as live context.

        Returns:
            Dict with keys: ``answer``, ``sources``, ``latency_ms``.
        """
        self._init_clients()
        started = time.monotonic()

        # ── Retrieve ──────────────────────────────────────────────────────────
        context_chunks: list[str] = []
        source_ids: list[str] = []

        if self._collection is not None:
            try:
                # Type-check satisfaction: capture result and count separately
                doc_count = self._collection.count() or 0
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(3, doc_count if doc_count > 0 else 1),
                )
                docs = results.get("documents", [[]])[0]
                ids = results.get("ids", [[]])[0]
                context_chunks = [str(d) for d in docs]
                source_ids = [str(i) for i in ids]
            except Exception as exc:
                logger.warning("ChromaDB query failed: %s", exc)

        # ── Compose prompt ────────────────────────────────────────────────────
        context_text = "\n\n".join(context_chunks) if context_chunks else "No additional context."
        live_context = (
            f"\n\nLive Sensor Reading: CO2 = {live_co2:.1f} ppm"
            if live_co2 is not None
            else ""
        )

        system_prompt = (
            "You are GreenFlow AI, an expert environmental monitoring assistant. "
            "Answer questions about CO2 levels, climate risk, and environmental actions "
            "using the context provided. Be concise, factual, and actionable. "
            "If you are unsure, say so clearly."
        )

        user_prompt = (
            f"Context:\n{context_text}{live_context}\n\n"
            f"Question: {query}\n\nAnswer:"
        )

        # ── Generate ──────────────────────────────────────────────────────────
        answer = "AI service is currently unavailable. Please check your OPENAI_API_KEY."

        if self._openai_client is not None and settings.OPENAI_API_KEY:
            try:
                response = await self._openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=512,
                    temperature=0.4,
                )
                answer = response.choices[0].message.content or answer
            except Exception as exc:
                logger.error("OpenAI completion failed: %s", exc)
                answer = f"AI query failed: {exc!s}"

        latency_ms = (time.monotonic() - started) * 1000

        return {
            "answer": answer.strip(),
            "sources": source_ids,
            "latency_ms": float(f"{latency_ms:.2f}"),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

rag_engine = RAGEngine()
