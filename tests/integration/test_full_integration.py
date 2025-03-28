"""Full integration test combining multiple components."""
import pytest
import uuid
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List, Protocol

from src import engine
from src.core.engine import Engine
from src.core.startup import StartupTask
from src.data.entity import BaseEntity
from src.data.repository import IRepository, Repository
from src.data.specification import Specification
from src.data.db_context import IDbContext, DbContext

# Define a Task entity for testing
class Task(BaseEntity):
    """Task entity for integration testing."""
    __tablename__ = "tasks"
    
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    priority: Mapped[int] = mapped_column(default=0)
    completed: Mapped[bool] = mapped_column(default=False)

# Define a Task repository interface
class ITaskRepository(IRepository[Task], Protocol):
    async def find_completed(self) -> List[Task]: ...
    async def find_by_priority(self, min_priority: int) -> List[Task]: ...
    async def complete_task(self, task_id: str) -> Optional[Task]: ...

# Task specifications
class CompletedTaskSpecification(Specification[Task]):
    def to_expression(self):
        return Task.completed == True

class HighPrioritySpecification(Specification[Task]):
    def __init__(self, min_priority: int):
        self.min_priority = min_priority
    
    def to_expression(self):
        return Task.priority >= self.min_priority

# Task repository implementation
class TaskRepository(Repository[Task], ITaskRepository):
    def __init__(self, session):
        super().__init__(session, Task)
    
    async def find_completed(self) -> List[Task]:
        return await self.find(CompletedTaskSpecification())
    
    async def find_by_priority(self, min_priority: int) -> List[Task]:
        return await self.find(HighPrioritySpecification(min_priority))
    
    async def complete_task(self, task_id: str) -> Optional[Task]:
        return await self.update(task_id, completed=True)

# Database initialization task
class TestDatabaseTask(StartupTask):
    """Task to initialize test database."""
    order = 30
    
    async def execute_async(self) -> None:
        """Asynchronously execute the task."""
        # Create in-memory database
        db_context = DbContext("sqlite+aiosqlite:///:memory:")
        await db_context.initialize()
        
        # Create tables
        async with db_context.begin_transaction():
            await db_context.execute(Task.metadata.create_all(bind=db_context._engine))
        
        # Register database context with engine
        engine.register(IDbContext, db_context)
        engine.register(DbContext, db_context)

@pytest.mark.asyncio
async def test_full_integration():
    """Full integration test with engine, repository, and database."""
    # Create a fresh engine
    test_engine = Engine()
    test_engine._started = False
    
    # Add database task
    db_task = TestDatabaseTask()
    await db_task.execute_async()  # Manually execute for test
    test_engine._started = True  # Mark as started
    
    # Register components with engine
    db_context = DbContext("sqlite+aiosqlite:///:memory:")
    await db_context.initialize()
    
    # Create tables
    async with db_context.begin_transaction():
        await db_context.execute(Task.metadata.create_all(bind=db_context._engine))
    
    # Register with engine
    test_engine.register(IDbContext, db_context)
    test_engine.register(DbContext, db_context)
    
    # Create and register task repository
    task_repo = TaskRepository(db_context.get_session())
    test_engine.register(ITaskRepository, task_repo)
    
    # Use the engine to resolve repository
    repo = test_engine.resolve(ITaskRepository)
    
    # Create some tasks
    task1 = await repo.create(
        title="High Priority Task",
        description="This is urgent",
        priority=3,
        due_date=datetime.now(UTC)
    )
    
    task2 = await repo.create(
        title="Medium Priority Task",
        description="This is important",
        priority=2
    )
    
    task3 = await repo.create(
        title="Low Priority Task",
        description="This can wait",
        priority=1
    )
    
    # Complete a task
    completed = await repo.complete_task(task2.id)
    assert completed.completed is True
    
    # Find completed tasks
    completed_tasks = await repo.find_completed()
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == task2.id
    
    # Find high priority tasks
    high_priority = await repo.find_by_priority(2)
    assert len(high_priority) == 2
    assert task1 in high_priority
    assert task2 in high_priority
    assert task3 not in high_priority
    
    # Find high priority incomplete tasks
    high_priority_spec = HighPrioritySpecification(2)
    incomplete_spec = Specification[Task]()
    incomplete_spec.to_expression = lambda: Task.completed == False
    
    combined_spec = high_priority_spec.and_(incomplete_spec)
    high_priority_incomplete = await repo.find(combined_spec)
    
    assert len(high_priority_incomplete) == 1
    assert high_priority_incomplete[0].id == task1.id
    
    # Clean up
    await db_context.close()
