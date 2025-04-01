"""
Basic Todo Example

This example demonstrates the core repository pattern with entity creation and injection.
"""
import asyncio
import uuid
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

from examples.domain.todo_entity import Todo
from examples.repository.todo_repository import ITodoRepository, CompletedTodoSpecification, TitleContainsSpecification
from openbiocure_corelib import engine

async def main():
    
    import logging

    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG to see all messages
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Output to console
        ]
    )

    # Get the engine logger specifically
    logger = logging.getLogger('openbiocure_corelib.core.engine')
    
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
    
    # Find completed todos using specification
    # The line `completed_todos = await todo_repository.find(CompletedTodoSpecification())` is calling
    # the `find` method on the `todo_repository` object with a `CompletedTodoSpecification` as an
    # argument. This is likely a way to retrieve a list of todos that are marked as completed based on
    # the criteria defined in the `CompletedTodoSpecification` class. The `find` method in the
    # repository is expected to return a list of todos that match the specified criteria.
    completed_todos = await todo_repository.find(CompletedTodoSpecification())
    print(f"Found {len(completed_todos)} completed todos")
    
    # Find todos by title
    learn_todos = await todo_repository.find(TitleContainsSpecification("Learn"))
    print(f"Found {len(learn_todos)} todos with 'Learn' in the title")

if __name__ == "__main__":
    asyncio.run(main())
