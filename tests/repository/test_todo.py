# tests/repository/test_todo.py
import pytest
from herpailib.entities.todo import Todo
from herpailib.infrastructure.repository.base_repository import BaseRepository

@pytest.mark.asyncio
async def test_todo_crud(session):
    # Arrange
    repo = BaseRepository[Todo](db=session, entity=Todo)
    
    # Act - Create
    todo = await repo.create(
        id="1",
        task="Test task"
    )
    
    # Assert - Create
    assert todo.id == "1"
    assert todo.task == "Test task"
    assert not todo.completed
    
    # Act & Assert - Get
    fetched = await repo.get("1")
    assert fetched is not None
    assert fetched.task == "Test task"
    
    # Act & Assert - Update
    updated = await repo.update("1", task="Updated task")
    assert updated is not None
    assert updated.task == "Updated task"
    
    # Act & Assert - Delete
    deleted = await repo.delete("1")
    assert deleted is True
    
    # Verify deletion
    none = await repo.get("1")
    assert none is None