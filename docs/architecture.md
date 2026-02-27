# GreenFlow AI – System Architecture

## Overview

GreenFlow AI is a six-layer real-time environmental monitoring system that ingests CO2 sensor data, enriches it through a streaming pipeline, stores it in a relational database, answers natural-language questions via a RAG engine, and presents everything through a browser-based dashboard.

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser / Client                         │
│   index.html · style.css · app.js · api.js · charts.js         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST / SSE
┌──────────────────────────▼──────────────────────────────────────┐
│                      FastAPI Application                        │
│   /api/v1/health  /events  /query  /stream  /risk               │
│   /prediction  /recommendation                                  │
└──────────────────────────┬──────────────────────────────────────┘
          ┌────────────────┼─────────────────┐
          │                │                 │
┌─────────▼──────┐ ┌───────▼──────┐ ┌───────▼──────────────┐
│  Streaming     │ │  RAG Engine  │ │    Services Layer     │
│  Pipeline      │ │  (ChromaDB + │ │  chatbot · analytics  │
│  (extractor +  │ │   OpenAI)    │ │  alerts               │
│  streaming.py) │ └──────────────┘ └──────────────────────┘
└─────────┬──────┘
          │
┌─────────▼──────────────────────────────────────────────────────┐
│              SQLAlchemy Async ORM                               │
│         Event · SystemAlert · QueryLog                          │
└─────────┬──────────────────────────────────────────────────────┘
          │
    SQLite (dev) / PostgreSQL (prod)
```

---

## Component Breakdown

| Component | Path | Responsibility |
|-----------|------|----------------|
| Configuration | `app/config.py` | Pydantic-settings from `.env` |
| Database | `app/database/` | ORM models, async session, init |
| Pipeline | `app/pipeline/` | Extractor (risk scoring) + JSONL streamer |
| RAG Engine | `app/rag/engine.py` | ChromaDB retrieval + OpenAI completion |
| Services | `app/services/` | Chatbot, Analytics, Alerts |
| API Routes | `app/api/` | FastAPI routers per concern |
| Frontend | `frontend/` | Vanilla HTML/CSS/JS dashboard |
| DevOps | `Dockerfile`, `docker-compose.yml`, `.github/` | Containerisation + CI |

---

## Data Flow

```
Sensor → POST /events → EventCreate schema validation
       → Feature extraction (risk, carbon, severity)
       → Persist to Event table
       → AlertService evaluates thresholds
       → SSE /stream/events pushes to dashboard

User → POST /query → ChatbotService
     → RAGEngine retrieves documents from ChromaDB
     → OpenAI generates grounded answer
     → QueryLog persisted
     → Answer returned to browser chat panel
```

---

## Technology Choices

| Technology | Reason |
|------------|--------|
| FastAPI | Async-first, auto-docs, pydantic integration |
| SQLAlchemy Async | Type-safe ORM, supports SQLite and PostgreSQL |
| ChromaDB | Lightweight embedded vector store, no infra required |
| OpenAI GPT-3.5-turbo | Best balance of cost and quality for RAG |
| SSE | Zero-dependency real-time push (no WebSocket infra) |
| Vanilla JS | No build step, instant browser compatibility |
| Docker | Reproducible, portable deployment |
