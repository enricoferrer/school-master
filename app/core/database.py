from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# ── Engine async ──────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,   
    pool_pre_ping=True,       # detecta conexões mortas automaticamente
    echo=False,               # True só em dev para ver as queries
)

# ── Session factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,   # evita lazy loads após commit em contexto async
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