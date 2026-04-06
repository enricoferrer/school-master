from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# ── Engine async (FastAPI) ──────────────────────────────────────────────────────
async_engine = create_async_engine(
    settings.database_url,   
    pool_pre_ping=True,
    echo=False, 
)

# ── Session factory async (FastAPI) ────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ── Engine síncrono (Celery workers) ────────────────────────────────────────────
# Converte a URL async (postgresql+asyncpg) para síncrona (postgresql+psycopg2)
sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
)
sync_engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

# ── Session factory síncrona (Celery workers) ─────────────────────────────────
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ── Base dos models ───────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ── Dependency do FastAPI ─────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise