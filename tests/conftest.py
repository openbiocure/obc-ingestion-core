# tests/conftest.py
import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from herpailib.infrastructure.db.base_entity import Base

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
def session_factory(test_engine):
    """Create a session factory."""
    return async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False
    )

@pytest_asyncio.fixture
async def session(session_factory) -> AsyncSession:
    """Create a new session for a test."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise