"""
Basic Todo Example

This example demonstrates the core repository pattern with entity creation and injection.
"""
import asyncio
import logging
import uuid
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

from examples.domain.todo_entity import Todo
from examples.repository.todo_repository import ITodoRepository, CompletedTodoSpecification, TitleContainsSpecification
from obc_ingestion_core import engine

async def main() -> None:

    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG to see all messages
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Output to console
        ]
    )

    # Get the engine logger specifically
    logger = logging.getLogger('obc_ingestion_core.core.engine')
    
    # Initialize and start the engine 
    engine.initialize()
    await engine.start()
    
    # Resolve the todo repository
    todo_repository =  engine.resolve(ITodoRepository)
    
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
    
    completed_todos = await todo_repository.find(CompletedTodoSpecification())
    print(f"Found {len(completed_todos)} completed todos")
    
    # Find todos by title
    learn_todos = await todo_repository.find(TitleContainsSpecification("Learn"))
    print(f"Found {len(learn_todos)} todos with 'Learn' in the title")

if __name__ == "__main__":
    asyncio.run(main())
