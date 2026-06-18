"""
Database engine + session setup (async SQLAlchemy 2.0).

Laravel hides all of this inside the framework. In Python you wire it explicitly
once, then reuse it everywhere. Three things live here:

  1. `engine`        — the connection pool to Postgres (created from DATABASE_URL).
  2. `SessionLocal`  — a factory that hands out DB sessions (a "session" ≈ a unit of
                       work / transaction, similar to Eloquent's underlying connection).
  3. `Base`          — the parent class all ORM models inherit from. SQLAlchemy
                       collects every table definition under Base.metadata, which
                       Alembic then reads to generate migrations.

You will rarely edit this file again.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# The async engine. Set SQL_ECHO=true in .env to log every SQL statement
# (handy while learning); it's off by default to keep the logs readable.
engine = create_async_engine(settings.database_url, echo=settings.sql_echo)

# Session factory. expire_on_commit=False keeps objects usable after commit
# (important when we return them from an endpoint after saving).
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for all ORM models (see models.py)."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a DB session and guarantees it's closed.

    This is the `Depends()` pattern (≈ Laravel's service container resolving a
    dependency). Endpoints declare `db: AsyncSession = Depends(get_db)` and get a
    ready-to-use session; the `async with` block closes it automatically after.
    """
    async with SessionLocal() as session:
        yield session
