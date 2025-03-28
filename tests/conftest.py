import pytest
import asyncio
from src import engine
from src.data.db_context import DbContext

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def initialized_engine():
    # Use in-memory SQLite for tests
    engine.register(DbContext, DbContext("sqlite+aiosqlite:///:memory:"))
    engine.initialize()
    engine.start()
    yield engine
