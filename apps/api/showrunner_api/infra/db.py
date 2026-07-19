from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from showrunner_api.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url or "postgresql+asyncpg://postgres:postgres@localhost/showrunner",
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def check_database() -> bool:
    async with engine.connect() as conn:
        await conn.exec_driver_sql("SELECT 1")
    return True
