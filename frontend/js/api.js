/**
 * GreenFlow AI – API Client Module
 *
 * Centralises all HTTP fetch calls to the backend.
 * All functions return Promises.  Never import from DOM here.
 */

const API_BASE = "/api/v1";

/**
 * Perform a GET request against the GreenFlow API.
 * @param {string} path
 * @returns {Promise<any>}
 */
async function apiGet(path) {
  const resp = await fetch(`${API_BASE}${path}`);
  if (!resp.ok) throw new Error(`GET ${path} → ${resp.status}`);
  return resp.json();
}

/**
 * Perform a POST request with a JSON body.
 * @param {string} path
 * @param {object} body
 * @returns {Promise<any>}
 */
async function apiPost(path, body) {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || `POST ${path} → ${resp.status}`);
  }
  return resp.json();
}

// ── Public API ────────────────────────────────────────────────────────────

/** @returns {Promise<object>} Health status */
const fetchHealth = () => apiGet("/health");

/** @returns {Promise<object[]>} Recent events list */
const fetchEvents = (limit = 20) => apiGet(`/events?limit=${limit}`);

/** @returns {Promise<object>} Current risk assessment */
const fetchRisk = () => apiGet("/risk");

/** @returns {Promise<object>} CO2 prediction */
const fetchPrediction = () => apiGet("/prediction");

/** @returns {Promise<object>} Recommendation */
const fetchRecommendation = () => apiGet("/recommendation");

/**
 * Send a query to the AI advisor.
 * @param {string} query
 * @returns {Promise<{answer: string, sources: string[], latency_ms: number}>}
 */
const postQuery = (query) => apiPost("/query", { query });
