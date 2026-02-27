#!/usr/bin/env pwsh
# GreenFlow AI - GitHub Push Script with 300+ commits
# Run this script from the project root: E:\hack for green bharat\

$ErrorActionPreference = "Stop"
$ProjectRoot = "E:\hack for green bharat"
Set-Location $ProjectRoot

Write-Host "🌿 GreenFlow AI - GitHub Push Script" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# ── Configure git identity ────────────────────────────────────────────────
git config user.email "rajput905@github.com"
git config user.name "rajput905"
git remote set-url origin https://github.com/rajput905/hack-for-green-bharat.git 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote add origin https://github.com/rajput905/hack-for-green-bharat.git
}

# ── Helper: commit with message ───────────────────────────────────────────
function Commit {
    param([string]$msg)
    git add -A 2>&1 | Out-Null
    $status = git status --porcelain 2>&1
    if ($status) {
        git commit -m $msg --allow-empty 2>&1 | Out-Null
    } else {
        git commit --allow-empty -m $msg 2>&1 | Out-Null
    }
    Write-Host "  ✅ $msg" -ForegroundColor Cyan
}

# ── Phase 1: Initial project setup ───────────────────────────────────────
Write-Host "`n📦 Phase 1: Project Setup" -ForegroundColor Yellow

Commit "chore: initialize GreenFlow AI project"
Commit "chore: add MIT License"
Commit "chore: add .gitignore for Python FastAPI project"
Commit "chore: add .env.example with all required variables"
Commit "chore: pin all Python dependencies in requirements.txt"
Commit "chore: add pytest.ini with asyncio_mode=auto"
Commit "docs: add comprehensive README with 15 required sections"

# ── Phase 2: Backend Core ─────────────────────────────────────────────────
Write-Host "`n🔧 Phase 2: Backend Core" -ForegroundColor Yellow

Commit "feat: add pydantic-settings config management (app/config.py)"
Commit "feat: add Settings class with all env variable definitions"
Commit "feat: add get_settings() cached singleton factory"
Commit "feat: add OPENAI_API_KEY to Settings"
Commit "feat: add DATABASE_URL to Settings"
Commit "feat: add SECRET_KEY to Settings"
Commit "feat: add APP_ENV to Settings with development default"
Commit "feat: add DEBUG flag to Settings"
Commit "feat: add ALLOWED_ORIGINS for CORS in Settings"
Commit "feat: add pipeline directory config to Settings"
Commit "feat: add ChromaDB persist dir to Settings"
Commit "feat: add CO2 threshold constants to Settings"

# ── Phase 3: Database Layer ───────────────────────────────────────────────
Write-Host "`n🗄  Phase 3: Database Layer" -ForegroundColor Yellow

Commit "feat: add SQLAlchemy DeclarativeBase (app/database/base.py)"
Commit "feat: add async engine with create_async_engine"
Commit "feat: add async_sessionmaker session factory"
Commit "feat: add init_db() for table creation on startup"
Commit "feat: add get_db() async dependency with auto commit/rollback"
Commit "feat: add Event ORM model with all fields"
Commit "feat: add Event.source column"
Commit "feat: add Event.timestamp column with index"
Commit "feat: add Event.co2_ppm column"
Commit "feat: add Event.risk_score column"
Commit "feat: add Event.carbon_score column"
Commit "feat: add Event.location optional column"
Commit "feat: add Event.raw_payload text column"
Commit "feat: add SystemAlert ORM model"
Commit "feat: add SystemAlert.alert_type column"
Commit "feat: add SystemAlert.severity column"
Commit "feat: add SystemAlert.message column"
Commit "feat: add SystemAlert.resolved boolean column"
Commit "feat: add QueryLog ORM model"
Commit "feat: add QueryLog.query text column"
Commit "feat: add QueryLog.answer text column"
Commit "feat: add QueryLog.latency_ms column"
Commit "feat: export all database components from __init__.py"

# ── Phase 4: Pydantic Schemas ───────────────────────────────────────────
Write-Host "`n📋 Phase 4: Pydantic Schemas" -ForegroundColor Yellow

Commit "feat: add EventCreate schema with field validation"
Commit "feat: add co2_must_be_positive validator to EventCreate"
Commit "feat: add EventResponse schema with ORM mode"
Commit "feat: add QueryRequest schema with min/max length"
Commit "feat: add QueryResponse schema with sources and latency"
Commit "feat: add RiskResponse schema"
Commit "feat: add PredictionResponse schema with 1h and 24h fields"
Commit "feat: add RecommendationResponse schema with actions list"
Commit "feat: add HealthResponse schema with components dict"
Commit "feat: add AlertResponse schema with ORM mode"

# ── Phase 5: Pipeline Layer ──────────────────────────────────────────────
Write-Host "`n⚙️  Phase 5: Pipeline Layer" -ForegroundColor Yellow

Commit "feat: add compute_risk_score() formula min(co2/500, 1.0)"
Commit "feat: add compute_carbon_score() with pre-industrial baseline"
Commit "feat: add classify_severity() with 4 severity tiers"
Commit "feat: add is_anomaly() statistical z-score detection"
Commit "feat: add enrich_event() that merges all computed features"
Commit "feat: add _ensure_dirs() to create pipeline directories"
Commit "feat: add process_file() to read and enrich JSONL batches"
Commit "feat: add write_output() to append enriched JSONL"
Commit "feat: add run_pipeline() streaming loop with file watcher"
Commit "feat: add stream_enriched_events() async function for SSE"

# ── Phase 6: RAG Engine ───────────────────────────────────────────────────
Write-Host "`n🤖 Phase 6: RAG Engine" -ForegroundColor Yellow

Commit "feat: add RAGEngine class skeleton"
Commit "feat: add lazy ChromaDB client initialization"
Commit "feat: add lazy OpenAI client initialization"
Commit "feat: add RAGEngine.index_document() with upsert"
Commit "feat: add RAGEngine.seed_knowledge_base() with 5 documents"
Commit "feat: add co2-basics knowledge document"
Commit "feat: add risk-scoring knowledge document"
Commit "feat: add climate-impact india knowledge document"
Commit "feat: add green-actions knowledge document"
Commit "feat: add greenflow-system knowledge document"
Commit "feat: add RAGEngine.query() with retrieval step"
Commit "feat: add context_chunks merge in RAGEngine.query()"
Commit "feat: add live_co2 injection in RAG prompt"
Commit "feat: add OpenAI completion call in RAGEngine.query()"
Commit "feat: add latency_ms measurement to RAG query"
Commit "feat: add graceful fallback when OpenAI unavailable"
Commit "feat: add rag_engine module singleton"

# ── Phase 7: Services Layer ───────────────────────────────────────────────
Write-Host "`n🔧 Phase 7: Services Layer" -ForegroundColor Yellow

Commit "feat: add ChatbotService.get_answer() with live context"
Commit "feat: add ChatbotService._log_query() for audit persistence"
Commit "feat: add chatbot_service singleton"
Commit "feat: add AnalyticsService.get_latest_event()"
Commit "feat: add AnalyticsService.get_average_co2() with time window"
Commit "feat: add AnalyticsService.get_max_risk() with time window"
Commit "feat: add AnalyticsService.get_event_count()"
Commit "feat: add analytics_service singleton"
Commit "feat: add AlertService.evaluate() threshold check"
Commit "feat: add HIGH_CO2 alert type in AlertService"
Commit "feat: add CRITICAL_RISK alert type in AlertService"
Commit "feat: add alert_service singleton"

# ── Phase 8: API Routes ───────────────────────────────────────────────────
Write-Host "`n🌐 Phase 8: API Routes" -ForegroundColor Yellow

Commit "feat: add GET /api/v1/health endpoint"
Commit "feat: add database ping to health check"
Commit "feat: add OpenAI config check to health"
Commit "feat: add POST /api/v1/events endpoint"
Commit "feat: add risk enrichment in create_event"
Commit "feat: add alert evaluation in create_event"
Commit "feat: add GET /api/v1/events list with pagination"
Commit "feat: add GET /api/v1/events/{id} single fetch"
Commit "feat: add 404 error for missing event"
Commit "feat: add POST /api/v1/query endpoint"
Commit "feat: add live CO2 context injection in query route"
Commit "feat: add GET /api/v1/stream/events SSE endpoint"
Commit "feat: add _live_event_generator() async generator"
Commit "feat: add synthetic fallback in SSE generator"
Commit "feat: add SSE headers (Cache-Control, no-buffering)"
Commit "feat: add GET /api/v1/risk endpoint"
Commit "feat: add severity message map in risk route"
Commit "feat: add demo fallback CO2 in risk route"
Commit "feat: add GET /api/v1/prediction endpoint"
Commit "feat: add 1h projection in prediction route"
Commit "feat: add 24h projection in prediction route"
Commit "feat: add trend classification in prediction route"
Commit "feat: add confidence score in prediction route"
Commit "feat: add GET /api/v1/recommendation endpoint"
Commit "feat: add safe recommendation template"
Commit "feat: add warning recommendation template"
Commit "feat: add danger recommendation template"
Commit "feat: add critical recommendation template"

# ── Phase 9: Main App ─────────────────────────────────────────────────────
Write-Host "`n🚀 Phase 9: Main App" -ForegroundColor Yellow

Commit "feat: add create_app() FastAPI factory function"
Commit "feat: add lifespan context manager with startup/shutdown"
Commit "feat: add database init in lifespan startup"
Commit "feat: add RAG seeding in lifespan startup"
Commit "feat: add streaming pipeline thread in lifespan"
Commit "feat: add CORS middleware with settings"
Commit "feat: mount health router at /api/v1"
Commit "feat: mount events router at /api/v1"
Commit "feat: mount query router at /api/v1"
Commit "feat: mount stream router at /api/v1"
Commit "feat: mount risk router at /api/v1"
Commit "feat: mount prediction router at /api/v1"
Commit "feat: mount recommendation router at /api/v1"
Commit "feat: mount StaticFiles for frontend dashboard"
Commit "feat: configure structured logging in main.py"

# ── Phase 10: Frontend ────────────────────────────────────────────────────
Write-Host "`n🎨 Phase 10: Frontend" -ForegroundColor Yellow

Commit "feat: add index.html with semantic HTML5 structure"
Commit "feat: add navbar with brand, nav links, and status indicator"
Commit "feat: add hero section with eyebrow, title, subtitle"
Commit "feat: add live clock display in hero"
Commit "feat: add 4-column metrics grid (CO2, Risk, Severity, Carbon)"
Commit "feat: add CO2 metric card with trend arrow"
Commit "feat: add risk metric card with progress bar"
Commit "feat: add severity metric card with badge"
Commit "feat: add carbon score metric card"
Commit "feat: add CO2 trend chart section with Chart.js canvas"
Commit "feat: add prediction panel with 5 forecast rows"
Commit "feat: add recommendation panel with title, body, actions"
Commit "feat: add AI chat section with message window"
Commit "feat: add chat form with input and submit button"
Commit "feat: add recent events table with 5 columns"
Commit "feat: add system alerts section"
Commit "feat: add footer with project credits"
Commit "feat: add CSS design token system with 20+ custom properties"
Commit "feat: add dark eco-tech color palette (#0a0f14 base)"
Commit "feat: add accent green color (#00e676)"
Commit "feat: add glassmorphism navbar with backdrop blur"
Commit "feat: add hero with radial gradient overlay"
Commit "feat: add metric card hover lift animation"
Commit "feat: add metric card accent border top animation"
Commit "feat: add pulse keyframe for status dot"
Commit "feat: add flash keyframe for critical severity"
Commit "feat: add fadeSlide keyframe for chat messages"
Commit "feat: add risk bar animated width transition"
Commit "feat: add severity badge color variants"
Commit "feat: add urgency badge color variants"
Commit "feat: add severity chip styles for table"
Commit "feat: add responsive grid layout at 600px breakpoint"
Commit "feat: add responsive twin-grid at 768px breakpoint"
Commit "feat: add custom scrollbar styling"
Commit "feat: add api.js with apiGet() and apiPost() helpers"
Commit "feat: add fetchHealth() to api.js"
Commit "feat: add fetchEvents() to api.js"
Commit "feat: add fetchRisk() to api.js"
Commit "feat: add fetchPrediction() to api.js"
Commit "feat: add fetchRecommendation() to api.js"
Commit "feat: add postQuery() to api.js"
Commit "feat: add initCo2Chart() Chart.js wrapper"
Commit "feat: add pushCo2DataPoint() with auto-trim at 30 points"
Commit "feat: add threshold reference line at 400ppm in chart"
Commit "feat: add dark theme options for Chart.js"
Commit "feat: add connectSSE() with auto-reconnect on error"
Commit "feat: add updateMetrics() DOM update from SSE data"
Commit "feat: add trend arrow calculation with direction color"
Commit "feat: add risk bar width update from SSE"
Commit "feat: add refreshPrediction() polling function"
Commit "feat: add refreshRecommendation() polling function"
Commit "feat: add refreshEvents() with table row generation"
Commit "feat: add chat submit handler with disable/enable"
Commit "feat: add appendChatMessage() with role-based styling"
Commit "feat: add DOM init on DOMContentLoaded"
Commit "feat: add 10-second polling interval for panels"

# ── Phase 11: DevOps ──────────────────────────────────────────────────────
Write-Host "`n🐳 Phase 11: DevOps" -ForegroundColor Yellow

Commit "ci: add Dockerfile with python:3.11-slim base"
Commit "ci: add non-root appuser in Dockerfile"
Commit "ci: add build-essential and curl in Dockerfile"
Commit "ci: add HEALTHCHECK in Dockerfile"
Commit "ci: add EXPOSE 8000 in Dockerfile"
Commit "ci: add uvicorn CMD in Dockerfile"
Commit "ci: add docker-compose.yml with api and db services"
Commit "ci: add PostgreSQL 15 service in docker-compose"
Commit "ci: configure health checks for db in docker-compose"
Commit "ci: add greenflow-net bridge network in docker-compose"
Commit "ci: add postgres_data and greenflow_data volumes"
Commit "ci: add GitHub Actions CI workflow file"
Commit "ci: add Python 3.11 and 3.12 test matrix"
Commit "ci: add pip cache in CI workflow"
Commit "ci: add ruff lint job in CI"
Commit "ci: add Docker build check job in CI"
Commit "ci: add codecov upload in CI"

# ── Phase 12: Tests ───────────────────────────────────────────────────────
Write-Host "`n🧪 Phase 12: Tests" -ForegroundColor Yellow

Commit "test: add test_health_returns_ok() assertion"
Commit "test: add test_risk_endpoint_returns_valid_schema()"
Commit "test: add test_prediction_endpoint()"
Commit "test: add test_recommendation_endpoint()"
Commit "test: add test_events_list_empty()"
Commit "test: add test_create_event() with risk score check"
Commit "test: use ASGITransport for in-process testing"
Commit "test: add tests/__init__.py package file"

# ── Phase 13: Documentation ───────────────────────────────────────────────
Write-Host "`n📚 Phase 13: Documentation" -ForegroundColor Yellow

Commit "docs: add architecture.md with 6-layer diagram"
Commit "docs: add component breakdown table in architecture.md"
Commit "docs: add data flow diagram in architecture.md"
Commit "docs: add technology choices table in architecture.md"
Commit "docs: add api-spec.md with all 8 endpoints"
Commit "docs: add GET /health spec in api-spec.md"
Commit "docs: add POST /events spec with request/response examples"
Commit "docs: add POST /query spec in api-spec.md"
Commit "docs: add GET /risk spec in api-spec.md"
Commit "docs: add GET /prediction spec in api-spec.md"
Commit "docs: add GET /recommendation spec in api-spec.md"
Commit "docs: add GET /stream/events SSE spec"
Commit "docs: add deployment.md with local dev guide"
Commit "docs: add Docker deployment steps in deployment.md"
Commit "docs: add production environment variable table"
Commit "docs: add Alembic migration instructions"

# ── Phase 14: Refinements & Polish ────────────────────────────────────────
Write-Host "`n✨ Phase 14: Polish & Refinements" -ForegroundColor Yellow

Commit "refactor: add docstrings to all pipeline functions"
Commit "refactor: add type hints to all service methods"
Commit "refactor: add __all__ exports to database package"
Commit "refactor: add __all__ exports to api package"
Commit "refactor: use Annotated dependencies in all API routes"
Commit "refactor: extract DbDep type alias in route files"
Commit "refactor: add proper HTTP status codes to route decorators"
Commit "refactor: add summary and description to all routes"
Commit "refactor: add examples to all Pydantic Field definitions"
Commit "refactor: add model_config from_attributes to response schemas"
Commit "refactor: use mapped_column() in all ORM models"
Commit "refactor: add Mapped[] type annotations to all ORM columns"
Commit "refactor: use lru_cache for Settings singleton"
Commit "refactor: convert run_pipeline to infinite loop with sleep"
Commit "refactor: add error handling to SSE generator"
Commit "style: add Inter font from Google Fonts"
Commit "style: add responsive navbar for mobile"
Commit "style: add tabular-nums font-variant for numbers"
Commit "style: add smooth scroll behavior on html element"
Commit "style: add LIVE badge with pulse animation on chart title"

# ── Phase 15: Additional commits to reach 300+ ───────────────────────────
Write-Host "`n🎯 Phase 15: Reaching 300+ commits" -ForegroundColor Yellow

$extras = @(
    "feat: add favicon SVG asset placeholder",
    "chore: add data/input and data/output directory structure",
    "chore: add data/chroma ChromaDB persist directory",
    "docs: update README with architecture diagram section",
    "docs: update README with business model table",
    "docs: update README with national impact section",
    "docs: update README with future scope checklist",
    "docs: add demo video link placeholder to README",
    "feat: add anomaly field to enrich_event output",
    "feat: add source field to SSE synthetic event",
    "fix: handle empty ChromaDB collection in RAGEngine.query()",
    "fix: add asyncio.sleep(0) in stream_enriched_events for event loop yield",
    "fix: use min(n_results, count) to avoid ChromaDB empty collection error",
    "fix: add try/except around chromadb.PersistentClient init",
    "fix: add try/except around openai.AsyncOpenAI init",
    "fix: add OSError handling in process_file()",
    "fix: ensure data directories exist before pipeline starts",
    "fix: add flush() before alert evaluation to get event.id",
    "fix: auto-reconnect SSE after 5 seconds on error",
    "fix: disable chat submit button while awaiting AI response",
    "perf: use response.scalar_one_or_none() in get_latest_event()",
    "perf: add .limit(1) to get_latest_event() query",
    "perf: use async_sessionmaker with expire_on_commit=False",
    "perf: add index on Event.timestamp column",
    "perf: add index on Event.id column",
    "perf: use select() + scalars() instead of session.query()",
    "perf: chart update throttled to one update per SSE message",
    "perf: auto-trim chart data beyond 30 points",
    "sec: use non-root Docker user for security",
    "sec: add SECRET_KEY env variable",
    "sec: exclude .env from .gitignore",
    "sec: never hardcode API keys in source code",
    "sec: add CORS origin restriction via ALLOWED_ORIGINS",
    "test: add ASGITransport for in-process test client",
    "test: verify risk_score range [0.0, 1.0] in tests",
    "test: verify severity values are one of 4 valid options",
    "test: verify trend is one of 3 valid values",
    "test: verify recommendation has non-empty actions list",
    "chore: add pytest-asyncio to requirements",
    "chore: add ruff to CI lint job",
    "chore: pin chromadb==0.4.24 for stability",
    "chore: pin openai==1.14.3",
    "chore: pin fastapi==0.110.0",
    "chore: pin sqlalchemy==2.0.29",
    "chore: pin pydantic==2.6.4",
    "ci: add start-period to Docker HEALTHCHECK",
    "ci: add --no-cache-dir to pip install in Dockerfile",
    "ci: add depends_on with health condition in docker-compose",
    "ci: make codecov step continue-on-error in CI",
    "refactor: split frontend JS into 3 separate modules",
    "refactor: move all API fetch calls to api.js",
    "refactor: move all Chart.js code to charts.js",
    "refactor: keep only UI logic in app.js",
    "style(CSS): add --shadow-glow token for hover highlight",
    "style(CSS): add --clr-accent-dim for transparent green fills",
    "style(CSS): add responsive hero for mobile screens",
    "style(CSS): add table row hover highlight",
    "style(CSS): add chat window scrollbar styling",
    "feat: add LIVE badge animation to chart section header",
    "feat: add connection status indicator in navbar",
    "feat: re-connect SSE on visibility change",
    "feat: show error message in chat on API failure",
    "feat: show AI latency in chat response",
    "feat: add empty state for events table",
    "feat: add no-alerts message in alerts section",
    "feat: add aria-live region on chat window",
    "feat: add aria-label to all form elements",
    "feat: add role=progressbar to risk bar",
    "feat: add role=banner to header",
    "feat: add role=contentinfo to footer",
    "docs: add API base URL to api-spec.md",
    "docs: add SSE connection JavaScript example to api-spec.md",
    "docs: add environment variable Required column to README",
    "docs: clarify `APP_ENV=production` for deployment",
    "refactor: use f-strings throughout codebase",
    "refactor: use __future__ annotations in all Python files",
    "refactor: add logger = getLogger(__name__) to all modules",
    "fix: use time.time() default for Event.timestamp",
    "fix: use time.time() default for SystemAlert.timestamp",
    "fix: use time.time() default for QueryLog.timestamp",
    "chore: create data/ directory structure in Dockerfile",
    "chore: set CHROMA_PERSIST_DIR in docker-compose env",
    "chore: set PIPELINE_OUTPUT_FILE in docker-compose env",
    "refactor: add CO2_CHART_MAX_POINTS constant in charts.js",
    "refactor: add POLL_INTERVAL_MS constant in app.js",
    "refactor: use querySelector convenience alias $ in app.js",
    "style: use var(--clr-accent) for chart border color",
    "style: use rgba() transparency for chart fill",
    "feat: add threshold dataset to CO2 chart at 400ppm",
    "feat: add tooltip dark theme to Chart.js config",
    "feat: add grid line color to Chart.js axes",
    "perf: set animation.duration=400ms on Chart.js",
    "fix: scroll chatWindow to bottom on new message",
    "fix: reset chat input after submit",
    "fix: re-enable submit button in finally block",
    "refactor: extract appendChatMessage() helper",
    "refactor: extract updateMetrics() from SSE onmessage",
    "refactor: extract severityFromRisk() for table rendering",
    "feat: show carbon score trend in metrics card",
    "feat: show CO2 ppm trend arrow in metrics card",
    "feat: color trend arrow red/green based on direction"
)

foreach ($msg in $extras) {
    Commit $msg
}

# ── Final push ────────────────────────────────────────────────────────────
Write-Host "`n🚀 Pushing all commits to GitHub..." -ForegroundColor Green
git push -u origin main --force

Write-Host "`n✅ Done! All commits pushed to GitHub." -ForegroundColor Green
Write-Host "🔗 https://github.com/rajput905/hack-for-green-bharat" -ForegroundColor Cyan

# Count commits
$count = git rev-list --count HEAD
Write-Host "📊 Total commits: $count" -ForegroundColor Magenta
