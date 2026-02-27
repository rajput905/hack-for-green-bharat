# GreenFlow AI – API Specification

Base URL: `http://localhost:8000/api/v1`

All request/response bodies use `application/json`.

---

## Endpoints

### GET /health
Check application health.

**Response 200:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development",
  "components": {
    "database": "ok",
    "openai": "configured"
  }
}
```

---

### POST /events
Ingest a new environmental sensor event.

**Request body:**
```json
{
  "source": "sensor-01",
  "co2_ppm": 420.5,
  "location": "Delhi",
  "timestamp": 1700000000.0
}
```

**Response 201:**
```json
{
  "id": 1,
  "source": "sensor-01",
  "timestamp": 1700000000.0,
  "co2_ppm": 420.5,
  "risk_score": 0.841,
  "carbon_score": 0.2014,
  "location": "Delhi"
}
```

---

### GET /events
List recent events. Query params: `limit` (1-500, default 50), `offset`.

---

### GET /events/{id}
Retrieve a specific event by ID.

---

### POST /query
Ask an environmental question to the AI.

**Request body:**
```json
{ "query": "What is the current CO2 risk level?" }
```

**Response 200:**
```json
{
  "answer": "Based on the current CO2 reading of 420 ppm...",
  "sources": ["co2-basics", "risk-scoring"],
  "latency_ms": 1234.5
}
```

---

### GET /risk
Get current environmental risk assessment.

**Response 200:**
```json
{
  "risk_score": 0.84,
  "risk_level": "danger",
  "co2_ppm": 420.5,
  "threshold": 400.0,
  "message": "🔴 Dangerous CO2 level detected. Take immediate action."
}
```

---

### GET /prediction
Get CO2 trend prediction.

**Response 200:**
```json
{
  "current_co2": 420.5,
  "predicted_co2_1h": 425.2,
  "predicted_co2_24h": 418.7,
  "trend": "stable",
  "confidence": 0.87
}
```

---

### GET /recommendation
Get AI-powered environmental action recommendations.

**Response 200:**
```json
{
  "title": "Dangerous CO2 Level – Act Now",
  "recommendation": "CO2 concentration is at dangerous levels...",
  "actions": ["Increase ventilation", "Suspend emissions"],
  "urgency": "high",
  "co2_context": 420.5
}
```

---

### GET /stream/events _(SSE)_
Subscribe to real-time environmental event stream.

Connect with `EventSource("/api/v1/stream/events")`.

Each SSE message data is a JSON object with:
```json
{
  "source": "live-sensor",
  "co2_ppm": 415.3,
  "risk_score": 0.83,
  "carbon_score": 0.187,
  "severity": "danger",
  "anomaly": false,
  "timestamp": 1700000015.0
}
```
Messages are pushed every ~2 seconds.
