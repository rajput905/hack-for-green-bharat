# GreenFlow AI – Deployment Guide

## Local Development

```bash
# 1. Clone the repository
git clone https://github.com/rajput905/hack-for-green-bharat.git
cd hack-for-green-bharat

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env – set OPENAI_API_KEY

# 5. Start the API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Open http://localhost:8000 in your browser
```

---

## Docker (Recommended)

```bash
# Build and run
cp .env.example .env
docker compose up --build

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## Production Deployment (Render / Railway / VPS)

### Environment variables required:
| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `DATABASE_URL` | PostgreSQL URL: `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | Random 64-character secret |
| `APP_ENV` | Set to `production` |

### Production Uvicorn command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### Health check URL: `GET /api/v1/health`

---

## Database Migrations

The application uses SQLAlchemy with `create_all` on startup.
For production, use Alembic for incremental migrations:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini to use settings.DATABASE_URL
alembic revision --autogenerate -m "initial"
alembic upgrade head
```
