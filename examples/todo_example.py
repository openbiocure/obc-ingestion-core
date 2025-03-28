import asyncio
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

# Import from your library
from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository
from src.data.specification import Specification

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

async def main():
    # Initialize and start the engine 
    # The engine internally handles service registration, DB setup, etc.
    engine.initialize()
    engine.start()
    
    # The engine auto-wires dependencies, just resolve what we need
    todo_repository = engine.resolve(ITodoRepository)
    
    # Create a todo
    todo = await todo_repository.create(
        title="Learn HerpAI-Lib",
        description="Implement repository pattern with dependency injection",
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
