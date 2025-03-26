# tests/repository/test_base.py

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from herpailib.infrastructure.db.base_entity import BaseEntity
from herpailib.infrastructure.repository.base_repository import BaseRepository
from herpailib.infrastructure.repository.interfaces import IRepository

class TestEntity(BaseEntity):
    __tablename__ = "test_entities"
    name: Mapped[str]

# Fixtures
@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_engine(event_loop):
    """Create a test database engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
def session_maker(test_engine):
    """Create a session maker."""
    return async_sessionmaker(test_engine, expire_on_commit=False)

@pytest_asyncio.fixture
async def db_session(session_maker) -> AsyncSession:
    """Create a session for each test."""
    async with session_maker() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def test_repo(db_session) -> IRepository[TestEntity]:
    """Provide a configured test repository."""
    return BaseRepository[TestEntity](db=db_session, entity=TestEntity)

# Test Cases
@pytest.mark.asyncio
async def test_repository_create(test_repo: IRepository[TestEntity]):
    """Test creating an entity."""
    created = await test_repo.create(id="1", name="test")
    
    # Verify
    assert created.id == "1"
    assert created.name == "test"
    assert isinstance(created.created_at, datetime)
    assert isinstance(created.updated_at, datetime)

@pytest.mark.asyncio
async def test_repository_get(test_repo: IRepository[TestEntity]):
    """Test getting an entity."""
    # Create test entity
    created = await test_repo.create(id="2", name="test get")
    
    # Get and verify
    fetched = await test_repo.get("2")
    assert fetched is not None
    assert fetched.id == "2"
    assert fetched.name == "test get"

@pytest.mark.asyncio
async def test_repository_update(test_repo: IRepository[TestEntity]):
    """Test updating an entity."""
    # Create test entity
    created = await test_repo.create(id="3", name="test update")
    
    # Update and verify
    updated = await test_repo.update("3", name="updated")
    assert updated is not None
    assert updated.id == "3"
    assert updated.name == "updated"
    
    # Verify updated_at changed
    assert updated.updated_at > updated.created_at

@pytest.mark.asyncio
async def test_repository_delete(test_repo: IRepository[TestEntity]):
    """Test deleting an entity."""
    # Create test entity
    created = await test_repo.create(id="4", name="test delete")
    
    # Delete and verify
    deleted = await test_repo.delete("4")
    assert deleted is True
    
    # Verify it's gone
    none = await test_repo.get("4")
    assert none is None