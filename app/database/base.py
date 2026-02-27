"""
GreenFlow AI - SQLAlchemy Declarative Base

All ORM models must import and extend this Base class.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy ORM models."""
    pass
