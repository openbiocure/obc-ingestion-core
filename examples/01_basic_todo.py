"""
Basic Todo Example

This example demonstrates the core repository pattern with entity creation and injection.
"""
import asyncio
import uuid
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository
from src.data.specification import Specification

# Define a Todo entity
class Todo(BaseEntity):
    """Todo entity for task management."""
    __tablename__ = "todos"
    
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)

# Define a Todo repository interface
class ITodoRepository(IRepository[Todo], Protocol):
    async def find_completed(self) -> List[Todo]: ...
    async def find_by_title(self, title: str) -> List[Todo]: ...

# Define specifications
class CompletedTodoSpecification(Specification[Todo]):
    def to_expression(self):
        return Todo.completed == True

class TitleContainsSpecification(Specification[Todo]):
    def __init__(self, text: str):
        self.text = text
    
    def to_expression(self):
        return Todo.title.contains(self.text)

async def main():
    # Initialize and start the engine 
    engine.initialize()
    engine.start()
    
    # Resolve the todo repository
    todo_repository = engine.resolve(ITodoRepository)
    
    # Create a Todo entity
    todo = Todo(
        id=str(uuid.uuid4()),
        title="Learn HerpAI-Lib",
        description="Implement repository pattern with dependency injection",
        completed=False
    )
    
    # Save the todo
    created_todo = await todo_repository.create(todo)
    print(f"Created Todo: {created_todo.title} (ID: {created_todo.id})")
    
    # Create another todo
    another_todo = Todo(
        title="Master HerpAI-Lib", 
        description="Build a complete application",
        completed=False
    )
    created_another = await todo_repository.create(another_todo)
    
    # Update a todo by marking it completed
    created_todo.completed = True
    updated_todo = await todo_repository.update(created_todo)
    print(f"Updated Todo: {updated_todo.title} (Completed: {updated_todo.completed})")
    
    # Find completed todos using specification
    completed_todos = await todo_repository.find(CompletedTodoSpecification())
    print(f"Found {len(completed_todos)} completed todos")
    
    # Find todos by title
    learn_todos = await todo_repository.find(TitleContainsSpecification("Learn"))
    print(f"Found {len(learn_todos)} todos with 'Learn' in the title")

if __name__ == "__main__":
    asyncio.run(main())
