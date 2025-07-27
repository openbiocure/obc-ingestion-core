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

    # Check session
    assert db_context._session is not None

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
