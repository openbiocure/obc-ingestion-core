"""Integration tests for DbContext and database operations."""

import pytest
from sqlalchemy import text

from obc_ingestion_core.data.db_context import DbContext


@pytest.mark.asyncio
async def test_db_context_initialization():
    """Test initializing the database context."""
    # Create in-memory database
    db_context = DbContext("sqlite+aiosqlite:///:memory:")

    # Initialize
    await db_context.initialize()

    # Check that the context is initialized (session factory should be available)
    assert db_context._session_factory is not None
    assert db_context._is_initialized is True

    # Test that we can get a session through the context manager
    async with db_context.session_context() as session:
        assert session is not None
        # Test that the session is working
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # Cleanup
    await db_context.close()


@pytest.mark.asyncio
async def test_db_context_transaction(in_memory_db):
    """Test transaction handling in the database context."""
    db_context = in_memory_db

    # Execute a statement directly (no transaction needed)
    await db_context.execute(
        text(
            "INSERT INTO test_entities (id, name, value, is_active) VALUES (:id, :name, :value, :is_active)"
        ),
        {"id": "test1", "name": "Test Entity", "value": 42, "is_active": 1},
    )

    # Query the entity
    result = await db_context.execute(
        text("SELECT * FROM test_entities WHERE id = :id"), {"id": "test1"}
    )
    row = result.fetchone()

    # Check result
    assert row is not None
    assert row.name == "Test Entity"
    assert row.value == 42
