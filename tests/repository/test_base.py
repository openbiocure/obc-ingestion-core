import sys
import os
sys.path.insert(0, os.path.abspath("."))

import pytest
import asyncio
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
from typing import Optional, AsyncGenerator
from herpailib.repository.base import BaseRepository


# --- Setup ---
class Base(DeclarativeBase):
    pass


class TestModel(Base):
    __tablename__ = "test_model"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]


class DummyDatabase:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def transaction(self):
        return self._session_factory()
    
    def session(self):
        return self._session_factory()


@pytest_asyncio.fixture(scope="module")
async def test_db() -> AsyncGenerator[DummyDatabase, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield DummyDatabase(session_factory)
    await engine.dispose()


@pytest.mark.asyncio
async def test_base_repository_crud(test_db):
    repo = BaseRepository[TestModel](db=test_db, model=TestModel)

    # Create
    created = await repo.create(id="1", name="test")
    assert created.id == "1"
    assert created.name == "test"

    # Get
    fetched = await repo.get("1")
    assert fetched is not None
    assert fetched.name == "test"

    # Update
    updated = await repo.update("1", name="updated")
    assert updated.name == "updated"

    # Delete
    deleted = await repo.delete("1")
    assert deleted is True

    # Confirm deletion
    none = await repo.get("1")
    assert none is None