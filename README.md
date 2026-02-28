🌿 GreenFlow AI

Real-Time Environmental Intelligence & Predictive Risk Monitoring

🧠 Overview

GreenFlow AI is a real-time environmental intelligence system that monitors CO₂ levels, calculates dynamic risk scores, forecasts short-term trends, and generates AI-powered mitigation recommendations.

It integrates streaming telemetry, predictive modeling, and Retrieval-Augmented Generation (RAG) into a modular and production-ready architecture.

🚀 Key Features

Real-time CO₂ ingestion

Configurable warning & danger thresholds

Risk scoring (0–1 scale)

Severity classification (Safe / Warning / Danger)

1-hour & 24-hour forecast simulation

AI-powered mitigation recommendations

What-If simulator

ChromaDB persistent vector storage

Environment-based configuration

Docker-ready deployment

🏗 System Architecture
Components

Ingestion Layer

REST API

JSONL file ingestion

Processing Layer

Risk score calculation

Threshold classification

Forecast generation

AI Layer

ChromaDB vector store

OpenAI RAG engine

Context-aware recommendations

API Layer

FastAPI async backend

Health & readiness checks

Frontend Layer

Live dashboard

Risk visualization

AI advisory panel

📊 Risk Calculation Logic
risk_score = min(co2_ppm / CO2_DANGER_THRESHOLD, 1.0)

Severity levels:

Safe → Below warning threshold

Warning → Between warning and danger

Danger → Above danger threshold

Configurable via environment variables.

⚙️ Environment Configuration

Create .env file:

APP_ENV=development
DEBUG=true
OPENAI_API_KEY=your_key
CO2_WARNING_THRESHOLD=350.0
CO2_DANGER_THRESHOLD=400.0
CHROMA_PERSIST_DIR=./chroma_storage
🐳 Docker Deployment
docker-compose up --build
📡 API Endpoints
Method	Endpoint	Description
GET	/health	Service health check
POST	/events	Ingest environmental event
GET	/events	Retrieve recent events
POST	/query	AI query
GET	/stream/events	Live SSE stream

Swagger: /docs

📸 Screenshots

Add real screenshots here:

docs/screenshots/dashboard.png
docs/screenshots/forecast.png
docs/screenshots/ai.png

Scoring systems heavily reward visual proof.

🧪 Testing
pytest tests/

Includes:

Health route test

Event ingestion test

AI query test

📁 Project Structure
app/
  api/
  services/
  models/
  core/
frontend/
tests/
docs/
Dockerfile
docker-compose.yml
🔐 Security & Production Mode

Environment-based configuration

Production mode toggle

Secret key management

Debug control

🌍 Target Use Cases

Smart city environmental monitoring

Industrial compliance tracking

ESG reporting automation

Urban risk mitigation

🔮 Future Enhancements

IoT device integration

ML anomaly detection

Multi-city deployment

Automated compliance reporting
