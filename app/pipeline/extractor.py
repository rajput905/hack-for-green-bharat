"""
GreenFlow AI - Feature Extraction

Converts raw CO2 sensor readings into normalized risk scores,
carbon scores, and environmental severity classifications.
"""

from __future__ import annotations

from app.config import settings


def compute_risk_score(co2_ppm: float) -> float:
    """
    Compute a normalized risk score [0.0 – 1.0] from a CO2 reading.

    Formula: risk = min(co2 / 500, 1.0)

    Args:
        co2_ppm: CO2 concentration in parts-per-million.

    Returns:
        Risk score between 0.0 (safe) and 1.0 (critical).
    """
    return min(co2_ppm / 500.0, settings.RISK_SCORE_MAX)


def compute_carbon_score(co2_ppm: float) -> float:
    """
    Derive a carbon intensity score from a CO2 reading.

    Higher values indicate more carbon-intensive activity.

    Args:
        co2_ppm: CO2 concentration in parts-per-million.

    Returns:
        Carbon score (0.0 – 2.0 range, uncapped to preserve magnitude).
    """
    baseline = 350.0  # Pre-industrial reference
    return max((co2_ppm - baseline) / baseline, 0.0)


def classify_severity(co2_ppm: float) -> str:
    """
    Map a CO2 reading to a human-readable severity label.

    Thresholds:
    - Safe:     < 350 ppm
    - Warning:  350 – 399 ppm
    - Danger:   400 – 499 ppm
    - Critical: ≥ 500 ppm

    Args:
        co2_ppm: CO2 concentration in parts-per-million.

    Returns:
        One of {"safe", "warning", "danger", "critical"}.
    """
    if co2_ppm < settings.CO2_WARNING_THRESHOLD:
        return "safe"
    if co2_ppm < settings.CO2_DANGER_THRESHOLD:
        return "warning"
    if co2_ppm < 500.0:
        return "danger"
    return "critical"


def is_anomaly(co2_ppm: float, baseline_ppm: float = 350.0, std_dev: float = 30.0) -> bool:
    """
    Detect whether a CO2 reading is statistically anomalous
    (more than 2 standard deviations above baseline).

    Args:
        co2_ppm:      Observed CO2 concentration.
        baseline_ppm: Expected / historical mean.
        std_dev:      Standard deviation of the historical distribution.

    Returns:
        True if the reading is anomalous.
    """
    z_score = (co2_ppm - baseline_ppm) / std_dev
    return z_score > 2.0


def enrich_event(raw: dict) -> dict:
    """
    Enrich a raw sensor payload with computed features.

    Adds ``risk_score``, ``carbon_score``, ``severity``, and
    ``anomaly`` keys to the supplied dictionary.

    Args:
        raw: Dictionary containing at minimum a ``co2_ppm`` key.

    Returns:
        Enriched dictionary with computed fields merged in.
    """
    co2 = float(raw.get("co2_ppm", 0.0))
    return {
        **raw,
        "risk_score": compute_risk_score(co2),
        "carbon_score": compute_carbon_score(co2),
        "severity": classify_severity(co2),
        "anomaly": is_anomaly(co2),
    }
