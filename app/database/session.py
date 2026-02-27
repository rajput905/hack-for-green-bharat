"""
GreenFlow AI - Database Session Management

Creates the async SQLAlchemy engine and session factory.
Use `get_db` as a FastAPI dependency to get a database session.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database.base import Base

# ── Engine ───────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def init_db() -> None:
    """
    Create all database tables on application startup.

    Called from the FastAPI lifespan context manager.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    Usage::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
