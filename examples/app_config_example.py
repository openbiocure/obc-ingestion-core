import asyncio
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

# Import from your library
from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository
from src.core.app_config_startup import AppConfigStartupTask
from src.config.dataclass_config import AppConfig, AgentConfig

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
    # Add startup task for AppConfig
    engine.add_startup_task(AppConfigStartupTask("config.yaml"))
    
    # Initialize and start the engine 
    engine.initialize()
    engine.start()
    
    # Get AppConfig
    app_config = AppConfig.get_instance()
    
    # Display agent configurations
    print("Agent Configurations:")
    for name, agent in app_config.agents.items():
        print(f"\n{name}:")
        print(f"  Model: {agent.model_provider}/{agent.model}")
        print(f"  Temperature: {agent.temperature}")
        print(f"  Max Tokens: {agent.max_tokens}")
        print(f"  Tags: {', '.join(agent.tags) if agent.tags else 'None'}")
        print(f"  Research Domain: {'Yes' if agent.is_research_domain else 'No'}")
    
    # Resolve repository and create todo
    try:
        todo_repository = engine.resolve(ITodoRepository)
        
        # Create a todo
        todo = await todo_repository.create(
            title="Test AppConfig Integration",
            description="Using dataclass-based configuration",
            completed=False
        )
        
        print(f"\nCreated Todo: {todo.title} (ID: {todo.id})")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Note: Repository operations require a valid database connection")

if __name__ == "__main__":
    asyncio.run(main())
