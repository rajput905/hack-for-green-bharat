🌿 GreenFlow AI
Real-Time Environmental Intelligence & Predictive Risk Monitoring System

Predict. Prevent. Protect.
Transforming environmental monitoring from reactive dashboards to proactive intelligence.

📌 Overview

GreenFlow AI is a real-time environmental intelligence platform designed to monitor CO₂ levels, assess environmental risk, forecast future trends, and generate AI-powered mitigation recommendations.

Unlike traditional dashboards that simply display data, GreenFlow AI predicts environmental risk before escalation and provides actionable insights for prevention.

Built using FastAPI, real-time streaming, vector search (ChromaDB), and OpenAI-powered Retrieval-Augmented Generation (RAG).

🚨 Problem Statement

Urban regions and industrial zones face increasing environmental volatility due to:

Rising pollution levels

Climate instability

Regulatory compliance pressure

Delayed reactive intervention systems

Current systems:

Only display historical metrics

Do not forecast short-term risk

Lack AI-based prevention guidance

Require manual interpretation

This leads to delayed mitigation and higher environmental risk.

💡 Our Solution

GreenFlow AI integrates:

Real-time telemetry ingestion

Configurable risk scoring engine

CO₂ forecasting

AI-driven environmental recommendations

Streaming dashboard

Persistent vector memory for contextual reasoning

The system proactively detects environmental threats and recommends corrective action before regulatory violation occurs.

🏗 Architecture Overview
System Layers
1️⃣ Data Ingestion

JSONL sensor ingestion

REST API event ingestion

Real-time streaming via SSE

2️⃣ Processing & Feature Layer

CO₂ normalization

Risk score calculation

Threshold-based severity detection

Configurable via environment variables

3️⃣ AI Intelligence Layer

ChromaDB persistent vector storage

OpenAI-powered RAG engine

Context-aware recommendation generation

4️⃣ API Layer

FastAPI async backend

Structured endpoints

Health and readiness checks

5️⃣ Frontend Dashboard

Real-time telemetry cards

Risk gauge visualization

Forecast analytics

AI advisory panel

Ask GreenFlow AI chatbot

🔬 Core Features

✔ Real-time CO₂ monitoring
✔ Configurable warning & danger thresholds
✔ Risk score (0.0 – 1.0 scale)
✔ Severity classification (Safe / Warning / Danger)
✔ 1-hour & 24-hour forecast simulation
✔ AI-powered mitigation recommendations
✔ Persistent vector search (ChromaDB)
✔ Environment-based configuration
✔ Production-ready FastAPI backend
✔ Docker-ready deployment

📊 Risk Scoring Model

Risk is calculated dynamically using configurable thresholds:

Risk Score = min(CO2_PPM / CO2_DANGER_THRESHOLD, 1.0)

Environment variables allow modification without code changes:

CO2_WARNING_THRESHOLD=350.0
CO2_DANGER_THRESHOLD=400.0

Severity categories:

Safe

Warning

Danger

🤖 AI Recommendation Engine

GreenFlow AI uses Retrieval-Augmented Generation (RAG) to:

Retrieve contextual environmental knowledge

Combine with real-time telemetry

Generate structured mitigation guidance

Example AI Output:

Increase ventilation

Reduce high-emission processes

Notify environmental authorities

Activate emergency air purification systems

🌍 Target Users

Smart City Administrations

Pollution Control Boards

Industrial Compliance Teams

Environmental Monitoring Agencies

Urban Infrastructure Planners

💰 Business Model

GreenFlow AI operates as a SaaS-based environmental intelligence platform:

Municipal monitoring subscription

Industrial compliance licensing

API-based environmental analytics

ESG reporting integration

Future expansion includes predictive disaster alerts and multi-city risk dashboards.

🚀 Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/rajput905/hack-for-green-bharat.git
cd hack-for-green-bharat
2️⃣ Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment

Create .env file:

APP_ENV=development
DEBUG=true
OPENAI_API_KEY=your_key
CO2_WARNING_THRESHOLD=350.0
CO2_DANGER_THRESHOLD=400.0
CHROMA_PERSIST_DIR=./chroma_storage
5️⃣ Run Application
uvicorn app.main:app --reload

Visit:

http://localhost:8000
📡 API Endpoints
Method	Endpoint	Description
GET	/health	Service health check
POST	/events	Ingest environmental event
GET	/events	Retrieve recent events
POST	/query	Ask AI engine
GET	/stream/events	Live SSE stream

Swagger docs available at:

/docs
🐳 Docker Deployment
docker-compose up --build

Production mode:

APP_ENV=production
DEBUG=false
🧪 Testing
pytest tests/

Basic API health and route validation included.

📁 Project Structure
app/
frontend/
tests/
docs/

Modular and scalable backend architecture.

📸 Screenshots

(Add screenshots here from your dashboard)

Example:

![Dashboard]
<img width="1658" height="777" alt="Screenshot 2026-02-27 094422" src="https://github.com/user-attachments/assets/21bbf5e6-6499-4b68-8083-4046891d108b" />
<img width="1920" height="1080" alt="Screenshot 2026-02-27 092056 - Copy" src="https://github.com/user-attachments/assets/a26c79de-7e2a-4602-8a96-4ef5cb75fa04" />

🔮 Future Enhancements

IoT sensor integration

Multi-city environmental monitoring

ML-based anomaly detection

PDF environmental report export

Regulatory compliance automation

🏆 Why GreenFlow AI Stands Out

GreenFlow AI is not just a monitoring dashboard.

It combines:

Real-time streaming

Predictive analytics

AI-driven decision intelligence

Configurable environmental risk modeling

Persistent contextual reasoning

Designed for scalable smart city infrastructure.

📜 License

MIT License © 2026 GreenFlow AI Team
