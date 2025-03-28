import asyncio
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column
import os

# Import from your library
from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository, Repository
from src.data.specification import Specification
from src.core.startup import ConfigurationStartupTask, StartupTask
from src.config.yaml_config import YamlConfig

# Define a custom startup task
class DatabaseSetupStartupTask(StartupTask):
    """Startup task to set up the database."""
    
    def execute(self) -> None:
        print("Preparing database...")
        # This would typically create tables, run migrations, etc.
        # For this example, we'll just print a message

# Define a Todo entity
class Todo(BaseEntity):
    __tablename__ = "todos"
    
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)

# Define a Todo repository interface
class ITodoRepository(IRepository[Todo], Protocol):
    async def find_completed(self) -> List[Todo]: ...
    async def find_by_title(self, title: str) -> List[Todo]: ...

# Define a Todo specification
class CompletedTodoSpecification(Specification[Todo]):
    def to_expression(self):
        return Todo.completed == True

class TitleContainsSpecification(Specification[Todo]):
    def __init__(self, text: str):
        self.text = text
    
    def to_expression(self):
        return Todo.title.contains(self.text)

# Define the TodoRepository implementation
class TodoRepository:
    def __init__(self, session):
        self._base_repo = Repository(session, Todo)
    
    async def create(self, **kwargs) -> Todo:
        return await self._base_repo.create(**kwargs)
    
    async def get(self, id: str) -> Optional[Todo]:
        return await self._base_repo.get(id)
    
    async def update(self, id: str, **kwargs) -> Optional[Todo]:
        return await self._base_repo.update(id, **kwargs)
    
    async def delete(self, id: str) -> bool:
        return await self._base_repo.delete(id)
    
    async def find(self, spec: Specification[Todo]) -> List[Todo]:
        return await self._base_repo.find(spec)
    
    async def find_completed(self) -> List[Todo]:
        return await self.find(CompletedTodoSpecification())
    
    async def find_by_title(self, title: str) -> List[Todo]:
        return await self.find(TitleContainsSpecification(title))

async def main():
    # Add startup tasks
    engine.add_startup_task(ConfigurationStartupTask("config.yaml"))
    engine.add_startup_task(DatabaseSetupStartupTask())
    
    # Initialize and start the engine 
    # This will execute all startup tasks
    engine.initialize()
    engine.start()
    
    # Access configuration
    config = YamlConfig.get_instance()
    db_config = config.get('database', {})
    print(f"Connected to database: {db_config.get('database')} on {db_config.get('host')}")
    
    # Print some agent configurations
    agents = config.get_agent_configs()
    print(f"Configured agents: {', '.join(agents.keys())}")
    
    # Resolve database context
    from src.data.db_context import DbContext
    db_context = engine.resolve(DbContext)
    
    # Create a repository
    todo_repo = TodoRepository(db_context.get_session())
    
    # Register repository with engine
    engine.register(ITodoRepository, todo_repo)
    
    # Resolve and use the repository
    todo_repository = engine.resolve(ITodoRepository)
    
    # Create a todo
    todo = await todo_repository.create(
        title="Learn HerpAI-Lib with Configuration",
        description="Implement configuration and startup tasks",
        completed=False
    )
    
    print(f"Created Todo: {todo.title} (ID: {todo.id})")
    
    # Update the todo
    updated_todo = await todo_repository.update(
        todo.id,
        completed=True
    )
    
    print(f"Updated Todo: {updated_todo.title} (Completed: {updated_todo.completed})")
    
    # Find completed todos
    completed_todos = await todo_repository.find_completed()
    print(f"Found {len(completed_todos)} completed todos")

if __name__ == "__main__":
    asyncio.run(main())
