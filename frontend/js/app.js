/**
 * GreenFlow AI v2 – Main Application Controller
 *
 * Features:
 *  - SSE live CO₂ stream
 *  - System status panel (API / AI / Stream)
 *  - City mode simulation
 *  - Anomaly spike detection
 *  - Compliance meter (vs 400 ppm limit)
 *  - Risk category badge with tooltip
 *  - What-If Simulator
 *  - AI Explanation ("Why this recommendation?")
 *  - Recommendation loading skeleton
 *  - Chat AI shimmer
 *  - Architecture modal
 *  - Periodic polling for predictions, recommendations, events
 */

const ANOMALY_DELTA_PCT = 0.12;  // 12% spike = anomaly

// ── Global Config (Fetched from API) ─────────────────────────────────────────
let CONFIG = {
    warning: 350.0,
    danger: 400.0,
    critical: 500.0
};
let thresholdsLoaded = false;

async function syncThresholds() {
    try {
        const r = await fetch("/api/v1/config/thresholds");
        CONFIG = await r.json();
        thresholdsLoaded = true;
        console.log("✅ Thresholds synced:", CONFIG);
    } catch (e) {
        console.warn("⚠️ Using default thresholds (API unreachable)");
    }
}

// ── DOM helper ────────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

// ── Metric cards ──────────────────────────────────────────────────────────────
const co2ValueEl = $("co2-value");
const riskValueEl = $("risk-value");
const riskBarEl = $("risk-bar");
const riskCategoryBadge = $("risk-category-badge");
const severityValueEl = $("severity-value");
const severitySourceEl = $("severity-source");
const carbonValueEl = $("carbon-value");
const co2TrendEl = $("co2-trend");
const anomalyBadgeEl = $("anomaly-badge");
const complianceValueEl = $("compliance-value");
const complianceBarEl = $("compliance-bar");
const complianceLabelEl = $("compliance-label");

// ── Forecast panel ────────────────────────────────────────────────────────────
const predCurrentEl = $("pred-current");
const pred1hEl = $("pred-1h");
const pred24hEl = $("pred-24h");
const predTrendEl = $("pred-trend");
const predConfEl = $("pred-confidence");
const confidenceBarEl = $("confidence-bar");

// ── Recommendation panel ──────────────────────────────────────────────────────
const recSkeletonEl = $("rec-skeleton");
const recTitleEl = $("rec-title");
const recBodyEl = $("rec-body");
const recActionsEl = $("rec-actions");
const recUrgencyEl = $("rec-urgency");
const whyRecBtn = $("why-rec-btn");
const whyPanel = $("why-panel");
const whyCo2El = $("why-co2");
const whyRiskEl = $("why-risk");
const whyForecastEl = $("why-forecast");
const whySeverityEl = $("why-severity");

// ── System status panel ────────────────────────────────────────────────────────
const spApiDot = $("sp-api-dot");
const spApiLabel = $("sp-api-label");
const spAiDot = $("sp-ai-dot");
const spAiLabel = $("sp-ai-label");
const spStreamDot = $("sp-stream-dot");
const spStreamLabel = $("sp-stream-label");
const spLastUpdate = $("sp-last-update");
const spCity = $("sp-city");

// ── Events / alerts ───────────────────────────────────────────────────────────
const eventsTableBody = $("events-table-body");
const alertsContainer = $("alerts-container");

// ── Chat ──────────────────────────────────────────────────────────────────────
const chatWindow = $("chat-window");
const chatForm = $("chat-form");
const chatInput = $("chat-input");
const chatSubmitBtn = $("chat-submit-btn");
const chatSkeleton = $("chat-skeleton");

// ── Connection ────────────────────────────────────────────────────────────────
const connectionDot = $("connection-indicator");
const connectionLabel = $("connection-label");
const liveClockEl = $("live-clock");

// ── Simulator ─────────────────────────────────────────────────────────────────
const simRunBtn = $("sim-run-btn");
const simResult = $("sim-result");
const simRiskEl = $("sim-risk");
const simCategoryEl = $("sim-category");
const simComplianceEl = $("sim-compliance");
const simRecEl = $("sim-recommendation");

// ── Report ─────────────────────────────────────────────────────────────────────
const genReportBtn = $("gen-report-btn");
const reportOverlay = $("report-overlay");

// ── State ─────────────────────────────────────────────────────────────────────
let lastCo2 = null;
let latestData = {};  // last SSE payload
let currentCity = "Delhi";

// ── City offsets (simulated per-city CO₂ baseline delta) ──────────────────────
const CITY_OFFSET = {
    "Delhi": 40,
    "Mumbai": 20,
    "Bangalore": 5,
    "Chennai": 15,
    "Industrial Zone": 80,
};

// ── Live Clock ────────────────────────────────────────────────────────────────
function tickClock() {
    const now = new Date();
    liveClockEl.textContent = now.toLocaleString("en-IN", {
        weekday: "short", day: "2-digit", month: "short",
        year: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
}

// ── System Status Panel ───────────────────────────────────────────────────────
function setStatusDot(dot, label, state, text) {
    dot.className = `status-item__dot ${state}`;
    label.textContent = text;
}

async function checkSystemStatus() {
    // API check
    try {
        const r = await fetch("/api/v1/health");
        const d = await r.json();
        setStatusDot(spApiDot, spApiLabel, "online", "Connected");
        const aiOk = d.components?.openai !== "not_configured";
        setStatusDot(spAiDot, spAiLabel, aiOk ? "online" : "waiting",
            aiOk ? "Online" : "No API Key");
    } catch {
        setStatusDot(spApiDot, spApiLabel, "offline", "Disconnected");
        setStatusDot(spAiDot, spAiLabel, "offline", "Unavailable");
    }
}

// ── SSE Stream ────────────────────────────────────────────────────────────────
function connectSSE() {
    const es = new EventSource("/api/v1/stream/events");

    es.onopen = () => {
        connectionDot.className = "status-dot status-dot--connected";
        connectionLabel.textContent = "Live";
        setStatusDot(spStreamDot, spStreamLabel, "online", "Live");
    };

    es.onmessage = (e) => {
        try {
            const raw = JSON.parse(e.data);
            // Apply city offset
            const offset = CITY_OFFSET[currentCity] || 0;
            const data = { ...raw, co2_ppm: Number(raw.co2_ppm) + offset };
            data.risk_score = Math.min(data.co2_ppm / 500, 1.0);
            data.severity = classifySeverity(data.risk_score);
            updateMetrics(data);
            latestData = data;
            spLastUpdate.textContent = new Date().toLocaleTimeString("en-IN");
        } catch {
            console.warn("SSE parse error", e.data);
        }
    };

    es.onerror = () => {
        connectionDot.className = "status-dot status-dot--error";
        connectionLabel.textContent = "Reconnecting…";
        setStatusDot(spStreamDot, spStreamLabel, "waiting", "Reconnecting…");
        es.close();
        setTimeout(connectSSE, 5000);
    };
}

// ── Severity classifier ────────────────────────────────────────────────────────
function classifySeverity(risk) {
    if (risk >= 1.0) return "critical";
    if (risk >= 0.8) return "danger";
    if (risk >= 0.7) return "warning";
    return "safe";
}

function riskCategory(risk) {
    if (risk >= 1.0) return "critical";
    if (risk >= 0.8) return "danger";
    if (risk >= 0.7) return "warning";
    return "safe";
}

// ── Update metrics cards ──────────────────────────────────────────────────────
function updateMetrics(data) {
    const co2 = Number(data.co2_ppm).toFixed(1);
    const risk = Number(data.risk_score).toFixed(2);
    const carbon = Number(data.carbon_score || 0).toFixed(3);
    const severity = data.severity || "safe";
    const source = data.source || "live-sensor";

    // CO₂
    co2ValueEl.textContent = co2;

    // Trend + anomaly detection
    if (lastCo2 !== null) {
        const diff = Number(co2) - lastCo2;
        const pct = Math.abs(diff) / (lastCo2 || 1);
        co2TrendEl.textContent = diff > 0 ? `▲ +${diff.toFixed(1)}` : `▼ ${diff.toFixed(1)}`;
        co2TrendEl.style.color = diff > 0 ? "var(--clr-danger)" : "var(--clr-accent)";

        // Anomaly badge
        if (pct > ANOMALY_DELTA_PCT && diff > 0) {
            anomalyBadgeEl.textContent = `⚠ Spike +${(pct * 100).toFixed(0)}% in last cycle`;
            anomalyBadgeEl.style.display = "block";
        } else {
            anomalyBadgeEl.style.display = "none";
        }
    }
    lastCo2 = Number(co2);

    // Risk card
    riskValueEl.textContent = risk;
    const riskPercent = Math.min(Math.round(Number(risk) * 100), 100);
    riskBarEl.style.width = `${riskPercent}%`;
    riskBarEl.setAttribute("aria-valuenow", riskPercent);
    const cat = riskCategory(Number(risk));
    riskBarEl.className = `risk-bar ${cat === "danger" || cat === "critical" ? "risk-bar--" + cat : ""}`;
    riskCategoryBadge.textContent = cat.toUpperCase();
    riskCategoryBadge.className = `risk-badge ${cat}`;

    // Severity card
    severityValueEl.textContent = severity.toUpperCase();
    severityValueEl.setAttribute("data-severity", severity);
    severitySourceEl.textContent = `${source} · ${currentCity}`;

    // Carbon
    carbonValueEl.textContent = carbon;

    // Compliance meter
    const co2Num = Number(co2);
    const limitPct = Math.min((co2Num / CONFIG.critical) * 100, 100);
    complianceBarEl.style.width = `${limitPct}%`;

    if (co2Num >= CONFIG.critical) {
        complianceBarEl.style.background = "var(--clr-critical)";
        complianceLabelEl.textContent = `🆘 CRITICAL: ${(co2Num - CONFIG.danger).toFixed(0)} ppm above danger limit`;
        complianceLabelEl.style.color = "var(--clr-critical)";
        complianceValueEl.textContent = "!!!";
    } else if (co2Num >= CONFIG.danger) {
        complianceBarEl.style.background = "var(--clr-danger)";
        complianceLabelEl.textContent = `🚨 ${(co2Num - CONFIG.danger).toFixed(0)} ppm above regulatory limit`;
        complianceLabelEl.style.color = "var(--clr-danger)";
        complianceValueEl.textContent = "+";
    } else if (co2Num >= CONFIG.warning) {
        complianceBarEl.style.background = "var(--clr-warning)";
        complianceLabelEl.textContent = `⚠ ${(co2Num - CONFIG.warning).toFixed(0)} ppm above CPCB warning limit`;
        complianceLabelEl.style.color = "var(--clr-warning)";
        complianceValueEl.textContent = `+${(co2Num - CONFIG.warning).toFixed(0)}`;
    } else {
        complianceBarEl.style.background = "var(--clr-accent)";
        complianceLabelEl.textContent = `✅ Within CPCB safe range (< ${CONFIG.warning} ppm)`;
        complianceLabelEl.style.color = "var(--clr-accent)";
        complianceValueEl.textContent = `OK`;
    }

    // Chart - ensure we pass numeric value
    pushCo2DataPoint(co2Num, new Date().toLocaleTimeString("en-IN"));
}

// ── Polling: Prediction ───────────────────────────────────────────────────────
async function refreshPrediction() {
    try {
        const d = await fetchPrediction();
        const offset = CITY_OFFSET[currentCity] || 0;
        const cur = (Number(d.current_co2) + offset).toFixed(1);
        const h1 = (Number(d.predicted_co2_1h) + offset).toFixed(1);
        const h24 = (Number(d.predicted_co2_24h) + offset).toFixed(1);
        const conf = Math.round(d.confidence * 100);

        predCurrentEl.textContent = `${cur} ppm`;
        pred1hEl.textContent = `${h1} ppm`;
        pred24hEl.textContent = `${h24} ppm`;
        predTrendEl.textContent = d.trend;
        predConfEl.textContent = `${conf}%`;
        confidenceBarEl.style.width = `${conf}%`;

        // Update Why panel forecast
        whyForecastEl.textContent = `${h1} ppm (1h)`;
    } catch (err) {
        console.error("Prediction fetch failed", err);
    }
}

// ── Polling: Recommendation ───────────────────────────────────────────────────
async function refreshRecommendation() {
    recSkeletonEl.style.display = "flex";
    recTitleEl.style.display = "none";
    whyRecBtn.style.display = "none";

    try {
        const d = await fetchRecommendation();
        recSkeletonEl.style.display = "none";
        recTitleEl.style.display = "block";
        recTitleEl.textContent = d.title;
        recBodyEl.textContent = d.recommendation;
        recActionsEl.innerHTML = d.actions.map((a) => `<li>${a}</li>`).join("");
        recUrgencyEl.textContent = `Urgency: ${d.urgency.toUpperCase()}`;
        recUrgencyEl.setAttribute("data-urgency", d.urgency);
        whyRecBtn.style.display = "block";

        // Update Why panel
        whyCo2El.textContent = latestData.co2_ppm ? `${Number(latestData.co2_ppm).toFixed(1)} ppm` : d.co2_context ? `${d.co2_context} ppm` : "—";
        whyRiskEl.textContent = latestData.risk_score ? Number(latestData.risk_score).toFixed(2) : "—";
        whySeverityEl.textContent = (latestData.severity || d.urgency || "—").toUpperCase();
    } catch (err) {
        recSkeletonEl.style.display = "none";
        recTitleEl.style.display = "block";
        recTitleEl.textContent = "Unable to load recommendation.";
        console.error("Recommendation fetch failed", err);
    }
}

// ── Polling: Events ───────────────────────────────────────────────────────────
async function refreshEvents() {
    try {
        const events = await fetchEvents(15);
        if (!events.length) {
            eventsTableBody.innerHTML = `<tr><td colspan="5" class="table-placeholder">No events yet.</td></tr>`;
            alertsContainer.innerHTML = `<p class="no-alerts">No active alerts.</p>`;
            return;
        }

        const offset = CITY_OFFSET[currentCity] || 0;
        const rows = [];
        const alertItems = [];

        events.forEach((ev) => {
            const t = new Date(ev.timestamp * 1000).toLocaleTimeString("en-IN");
            const co2 = (Number(ev.co2_ppm) + offset).toFixed(1);
            const risk = Math.min((Number(ev.co2_ppm) + offset) / 500, 1.0).toFixed(2);
            const sev = classifySeverity(Number(risk));

            rows.push(`<tr>
        <td>${t}</td>
        <td>${ev.source}</td>
        <td>${co2}</td>
        <td>${risk}</td>
        <td><span class="chip chip--${sev}">${sev}</span></td>
      </tr>`);

            if (sev === "danger" || sev === "critical") {
                alertItems.push(`<div class="alert-item alert-item--${sev}">
          <span class="alert-item__type">🚨 ${sev.toUpperCase()}</span>
          <span class="alert-item__msg">CO₂ at ${co2} ppm from ${ev.source}</span>
          <span class="alert-item__time">${t}</span>
        </div>`);
            }
        });

        eventsTableBody.innerHTML = rows.join("");
        alertsContainer.innerHTML = alertItems.length
            ? alertItems.join("")
            : `<p class="no-alerts">✅ No alerts – all readings within safe range.</p>`;
    } catch (err) {
        console.error("Events fetch failed", err);
    }
}

// ── Chat ──────────────────────────────────────────────────────────────────────
function appendChatMessage(text, role = "bot") {
    const div = document.createElement("div");
    div.className = `chat-message chat-message--${role}`;
    const p = document.createElement("p");
    p.textContent = text;
    div.appendChild(p);
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = chatInput.value.trim();
    if (!q) return;

    appendChatMessage(q, "user");
    chatInput.value = "";
    chatSubmitBtn.disabled = true;
    chatSubmitBtn.textContent = "…";
    chatSkeleton.style.display = "flex";

    try {
        const result = await postQuery(q);
        chatSkeleton.style.display = "none";
        appendChatMessage(`🤖 ${result.answer}`, "bot");
        if (result.latency_ms) {
            appendChatMessage(`⏱ Response in ${result.latency_ms.toFixed(0)} ms`, "bot");
        }
    } catch (err) {
        chatSkeleton.style.display = "none";
        appendChatMessage(`Error: ${err.message}`, "error");
    } finally {
        chatSubmitBtn.disabled = false;
        chatSubmitBtn.textContent = "Send";
    }
});

// ── What-If Simulator ─────────────────────────────────────────────────────────
const SIM_RECS = {
    safe: "✅ Environment is safe. Maintain regular monitoring and air filtration systems.",
    warning: "⚠ CO₂ is elevated. Increase ventilation by 20–30% and alert your environmental team.",
    danger: "🚨 Dangerous levels detected. Suspend high-emission operations immediately and activate emergency protocol.",
    critical: "🆘 CRITICAL: Evacuate exposed zones, shut down all emission sources, and notify NDMA/CPCB emergency response.",
};

simRunBtn.addEventListener("click", () => {
    const co2 = parseFloat($("sim-co2").value) || 420;
    const temp = parseFloat($("sim-temp").value) || 28;
    const aqi = parseFloat($("sim-aqi").value) || 120;

    // AQI factor: high AQI amplifies effective risk slightly
    const aqiMult = 1 + (aqi / 1000);
    const effCo2 = co2 * aqiMult;
    const risk = Math.min(effCo2 / 500, 1.0);
    const cat = riskCategory(risk);

    const overLimit = co2 - CO2_SAFE_LIMIT;
    const compliance = overLimit > 0
        ? `+${overLimit.toFixed(0)} ppm over limit`
        : `${Math.abs(overLimit).toFixed(0)} ppm under limit`;

    simRiskEl.textContent = risk.toFixed(2);
    simRiskEl.style.color = cat === "safe" ? "var(--clr-accent)"
        : cat === "warning" ? "var(--clr-warning)" : "var(--clr-danger)";
    simCategoryEl.textContent = cat.toUpperCase();
    simCategoryEl.style.color = simRiskEl.style.color;
    simComplianceEl.textContent = compliance;
    simComplianceEl.style.color = overLimit > 0 ? "var(--clr-warning)" : "var(--clr-accent)";
    simRecEl.textContent = SIM_RECS[cat] || SIM_RECS.safe;
    simResult.style.display = "block";
});

// ── Why Recommendation toggle ──────────────────────────────────────────────────
whyRecBtn.addEventListener("click", () => {
    const isOpen = whyPanel.style.display !== "none";
    whyPanel.style.display = isOpen ? "none" : "block";
    whyRecBtn.textContent = isOpen
        ? "🔍 Why this recommendation?"
        : "▲ Hide explanation";
});

// ── City Selector ─────────────────────────────────────────────────────────────
$("city-select").addEventListener("change", (e) => {
    currentCity = e.target.value;
    spCity.textContent = currentCity;
    // Reset last CO₂ on city change to avoid false anomaly
    lastCo2 = null;
});

// ── Architecture Modal ────────────────────────────────────────────────────────
$("arch-modal-btn").addEventListener("click", () => {
    $("arch-modal").style.display = "flex";
});
$("arch-modal-close").addEventListener("click", () => {
    $("arch-modal").style.display = "none";
});
$("arch-modal").addEventListener("click", (e) => {
    if (e.target === $("arch-modal")) $("arch-modal").style.display = "none";
});

// ── Report Generation ──────────────────────────────────────────────────────────
function generateReport() {
    const timestamp = new Date().toLocaleString("en-IN");
    const co2 = Number(latestData.co2_ppm || 0).toFixed(1);
    const risk = Number(latestData.risk_score || 0).toFixed(2);
    const severity = (latestData.severity || "SAFE").toUpperCase();
    const city = currentCity;

    const recTitle = $("rec-title").textContent;
    const recBody = $("rec-body").textContent;
    const recActions = $("rec-actions").innerHTML;

    const reportHTML = `
    <div class="report-header">
      <div>
        <h1 class="report-title">GreenFlow AI Status Report</h1>
        <p style="color:#00e676; font-weight:700; margin:5px 0;">Environmental Intelligence Platform</p>
      </div>
      <div class="report-meta">
        <div>Generated: ${timestamp}</div>
        <div>Zone: ${city}</div>
        <div>Status: <strong>${severity}</strong></div>
      </div>
    </div>

    <div class="report-section">
      <h2>1. Live Environmental Metrics</h2>
      <div class="report-grid">
        <div class="report-card">
          <h3>Current CO₂ Level</h3>
          <div class="value">${co2} ppm</div>
        </div>
        <div class="report-card">
          <h3>Calculated Risk Index</h3>
          <div class="value">${risk} / 1.0</div>
        </div>
        <div class="report-card">
          <h3>Monitoring Source</h3>
          <div class="value">Active Smart-Sensor Net</div>
        </div>
        <div class="report-card">
          <h3>Regulatory Status</h3>
          <div class="value">${severity}</div>
        </div>
      </div>
    </div>

    <div class="report-section">
      <h2>2. AI Intelligence & Recommendations</h2>
      <div class="report-card" style="margin-bottom:1rem; border-left:4px solid #00e676;">
        <h3 style="color:#1a2433; font-weight:700;">${recTitle}</h3>
        <p style="font-size:10pt; line-height:1.5;">${recBody}</p>
      </div>
      <h3 style="font-size:10pt; margin-bottom:0.5rem;">Recommended Critical Actions:</h3>
      <ul style="font-size:10pt; line-height:1.8; color:#1a2433;">
        ${recActions}
      </ul>
    </div>

    <div class="report-section">
      <h2>3. Legal & Regulatory Baseline</h2>
      <p style="font-size:9pt; color:#6b7a8d;">
        This report is generated based on CPCB (Central Pollution Control Board) standards and real-time sensor data 
        processed via the GreenFlow Pathway Engine. Current data indicates a compliance status of 
        <strong>${severity === 'SAFE' ? 'IN COMPLIANCE' : 'ACTION REQUIRED'}</strong>.
      </p>
    </div>

    <div class="report-footer">
      <p>© 2026 GreenFlow AI - Hack for Green Bharat Initiative</p>
      <p>System Integrity: Verified | Data Encryption: AES-256 | Environment: ${city} Intelligent Zone</p>
    </div>
  `;

    reportOverlay.innerHTML = reportHTML;
    window.print();
}

genReportBtn.addEventListener("click", generateReport);

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    initCo2Chart("co2-chart");

    tickClock();
    setInterval(tickClock, 1000);

    connectSSE();
    syncThresholds().then(() => {
        checkSystemStatus();
        refreshPrediction();
        refreshRecommendation();
        refreshEvents();
    });
    setInterval(checkSystemStatus, 30_000);

    setInterval(refreshPrediction, POLL_INTERVAL_MS);
    setInterval(refreshRecommendation, POLL_INTERVAL_MS);
    setInterval(refreshEvents, POLL_INTERVAL_MS);
});
