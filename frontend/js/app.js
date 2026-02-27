/**
 * GreenFlow AI – Main Application Controller
 *
 * Orchestrates:
 * - SSE connection for live CO2 updates.
 * - Periodic polling for risk, prediction, recommendation, events.
 * - Chat form submission and DOM updates.
 * - Live clock.
 */

// ── Constants ────────────────────────────────────────────────────────────────
const POLL_INTERVAL_MS = 10_000; // 10 seconds for panel refresh

// ── DOM refs ─────────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const co2ValueEl = $("co2-value");
const riskValueEl = $("risk-value");
const riskBarEl = $("risk-bar");
const severityValueEl = $("severity-value");
const severitySourceEl = $("severity-source");
const carbonValueEl = $("carbon-value");
const co2TrendEl = $("co2-trend");

const predCurrentEl = $("pred-current");
const pred1hEl = $("pred-1h");
const pred24hEl = $("pred-24h");
const predTrendEl = $("pred-trend");
const predConfEl = $("pred-confidence");

const recTitleEl = $("rec-title");
const recBodyEl = $("rec-body");
const recActionsEl = $("rec-actions");
const recUrgencyEl = $("rec-urgency");

const eventsTableBody = $("events-table-body");
const alertsContainer = $("alerts-container");
const chatWindow = $("chat-window");
const chatForm = $("chat-form");
const chatInput = $("chat-input");
const chatSubmitBtn = $("chat-submit-btn");
const connectionDot = $("connection-indicator");
const connectionLabel = $("connection-label");
const liveClockEl = $("live-clock");

// ── Live Clock ────────────────────────────────────────────────────────────────
function tickClock() {
    const now = new Date();
    liveClockEl.textContent = now.toLocaleString("en-IN", {
        weekday: "short",
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

// ── SSE Stream ────────────────────────────────────────────────────────────────
let lastCo2 = null;

function connectSSE() {
    const es = new EventSource("/api/v1/stream/events");

    es.onopen = () => {
        connectionDot.className = "status-dot status-dot--connected";
        connectionLabel.textContent = "Live";
    };

    es.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            updateMetrics(data);
        } catch {
            console.warn("SSE parse error", e.data);
        }
    };

    es.onerror = () => {
        connectionDot.className = "status-dot status-dot--error";
        connectionLabel.textContent = "Reconnecting…";
        es.close();
        setTimeout(connectSSE, 5000);
    };
}

/** Update the metrics cards from an SSE payload. */
function updateMetrics(data) {
    const co2 = Number(data.co2_ppm).toFixed(1);
    const risk = Number(data.risk_score).toFixed(2);
    const carbon = Number(data.carbon_score).toFixed(3);
    const severity = data.severity || "safe";
    const source = data.source || "live-sensor";

    // CO2 card
    co2ValueEl.textContent = co2;

    // Trend arrow
    if (lastCo2 !== null) {
        const diff = Number(co2) - lastCo2;
        co2TrendEl.textContent = diff > 0 ? `▲ +${diff.toFixed(1)}` : `▼ ${diff.toFixed(1)}`;
        co2TrendEl.style.color = diff > 0 ? "var(--clr-danger)" : "var(--clr-accent)";
    }
    lastCo2 = Number(co2);

    // Risk card
    riskValueEl.textContent = risk;
    const riskPercent = Math.min(Math.round(Number(risk) * 100), 100);
    riskBarEl.style.width = `${riskPercent}%`;
    riskBarEl.setAttribute("aria-valuenow", riskPercent);
    riskBarEl.className = "risk-bar" + (severity === "critical" ? " risk-bar--critical" : severity === "danger" ? " risk-bar--danger" : "");

    // Severity card
    severityValueEl.textContent = severity.toUpperCase();
    severityValueEl.setAttribute("data-severity", severity);
    severitySourceEl.textContent = source;

    // Carbon card
    carbonValueEl.textContent = carbon;

    // Chart
    const timeLabel = new Date().toLocaleTimeString("en-IN");
    pushCo2DataPoint(Number(co2), timeLabel);
}

// ── Polling ───────────────────────────────────────────────────────────────────

async function refreshPrediction() {
    try {
        const d = await fetchPrediction();
        predCurrentEl.textContent = `${d.current_co2} ppm`;
        pred1hEl.textContent = `${d.predicted_co2_1h} ppm`;
        pred24hEl.textContent = `${d.predicted_co2_24h} ppm`;
        predTrendEl.textContent = d.trend;
        predConfEl.textContent = `${Math.round(d.confidence * 100)}%`;
    } catch (err) {
        console.error("Prediction fetch failed", err);
    }
}

async function refreshRecommendation() {
    try {
        const d = await fetchRecommendation();
        recTitleEl.textContent = d.title;
        recBodyEl.textContent = d.recommendation;
        recActionsEl.innerHTML = d.actions.map((a) => `<li>${a}</li>`).join("");
        recUrgencyEl.textContent = d.urgency;
        recUrgencyEl.setAttribute("data-urgency", d.urgency);
    } catch (err) {
        console.error("Recommendation fetch failed", err);
    }
}

async function refreshEvents() {
    try {
        const events = await fetchEvents(15);
        if (!events.length) {
            eventsTableBody.innerHTML = `<tr><td colspan="5" class="table-placeholder">No events yet.</td></tr>`;
            return;
        }
        eventsTableBody.innerHTML = events.map((ev) => {
            const t = new Date(ev.timestamp * 1000).toLocaleTimeString("en-IN");
            const sev = ev.severity || severityFromRisk(ev.risk_score);
            return `<tr>
        <td>${t}</td>
        <td>${ev.source}</td>
        <td>${Number(ev.co2_ppm).toFixed(1)}</td>
        <td>${Number(ev.risk_score).toFixed(2)}</td>
        <td><span class="chip chip--${sev}">${sev}</span></td>
      </tr>`;
        }).join("");
    } catch (err) {
        console.error("Events fetch failed", err);
    }
}

function severityFromRisk(risk) {
    if (risk >= 1.0) return "critical";
    if (risk >= 0.8) return "danger";
    if (risk >= 0.7) return "warning";
    return "safe";
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

    try {
        const result = await postQuery(q);
        appendChatMessage(`🤖 ${result.answer}`, "bot");
        if (result.latency_ms) {
            appendChatMessage(`⏱ ${result.latency_ms.toFixed(0)} ms`, "bot");
        }
    } catch (err) {
        appendChatMessage(`Error: ${err.message}`, "error");
    } finally {
        chatSubmitBtn.disabled = false;
        chatSubmitBtn.textContent = "Send";
    }
});

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    // Chart
    initCo2Chart("co2-chart");

    // Clock
    tickClock();
    setInterval(tickClock, 1000);

    // SSE
    connectSSE();

    // Initial data load
    refreshPrediction();
    refreshRecommendation();
    refreshEvents();

    // Periodic refresh
    setInterval(refreshPrediction, POLL_INTERVAL_MS);
    setInterval(refreshRecommendation, POLL_INTERVAL_MS);
    setInterval(refreshEvents, POLL_INTERVAL_MS);
});
