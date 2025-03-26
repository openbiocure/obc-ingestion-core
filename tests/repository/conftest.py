# tests/repository/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from herpailib.infrastructure.repository.base_entity import Base
from herpailib.infrastructure.repository.base_repository import BaseRepository
from herpailib.infrastructure.repository.interfaces import IRepository
from herpailib.entities.todo import Todo

@pytest_asyncio.fixture
async def todo_repo(session: AsyncSession) -> IRepository[Todo]:
    return BaseRepository[Todo](db=session, entity=Todo)