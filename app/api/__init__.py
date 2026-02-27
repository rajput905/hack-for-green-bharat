"""
GreenFlow AI - API Package

Registers all API route modules for convenient import in main.py.
"""

from app.api import events, health, prediction, query, recommendation, risk, stream

__all__ = [
    "health",
    "events",
    "query",
    "stream",
    "risk",
    "prediction",
    "recommendation",
]
