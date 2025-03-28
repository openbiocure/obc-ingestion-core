#!/bin/bash

# Create examples directory
mkdir -p examples

# 1. Basic Todo Example
cat > examples/01_basic_todo.py << 'EOF'
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
EOF

# 2. YAML Configuration Example
cat > examples/02_yaml_config.py << 'EOF'
"""
YAML Configuration Example

This example demonstrates how to use the YAML configuration
system with dotted access.
"""
import asyncio
from src import engine
from src.config.yaml_config import YamlConfig

async def main():
    # Initialize and start the engine with auto-discovered tasks
    engine.initialize()
    engine.start()
    
    # Get the configuration
    config = engine.resolve(YamlConfig)
    
    # Access configuration using dot notation
    print("YAML Configuration Example:")
    print("===========================")
    
    print("\nDatabase Configuration:")
    print(f"Host: {config.get('database.host')}")
    print(f"Port: {config.get('database.port')}")
    print(f"Database: {config.get('database.database')}")
    
    print("\nDefault Model Provider:")
    print(f"{config.get('app.default_model_provider')}")
    
    print("\nAgent Configurations:")
    for agent_name in config.get('app.agents', {}).keys():
        print(f"\n{agent_name}:")
        agent_config = config.get(f'app.agents.{agent_name}')
        print(f"  Model: {agent_config.get('model')}")
        print(f"  Temperature: {agent_config.get('temperature')}")
        print(f"  Tags: {', '.join(agent_config.get('tags', []))}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 3. AppConfig Example
cat > examples/03_app_config.py << 'EOF'
"""
AppConfig Example

This example demonstrates how to use the strongly-typed
AppConfig with dataclasses for configuration.
"""
import asyncio
from src import engine
from src.config.dataclass_config import AppConfig

async def main():
    # Initialize and start the engine with auto-discovered tasks
    engine.initialize()
    engine.start()
    
    # Get the typed configuration
    app_config = AppConfig.get_instance()
    
    print("AppConfig Example:")
    print("=================")
    
    print(f"\nDefault Model Provider: {app_config.default_model_provider}")
    
    print("\nDatabase Configuration:")
    if app_config.db_config:
        print(f"Connection String: {app_config.db_config.connection_string}")
        print(f"Dialect: {app_config.db_config.dialect}")
        print(f"Driver: {app_config.db_config.driver}")
    else:
        print("No database configuration found")
    
    print("\nAgent Configurations:")
    for name, agent in app_config.agents.items():
        print(f"\n{name}:")
        print(f"  Model Provider: {agent.model_provider}")
        print(f"  Model: {agent.model}")
        print(f"  Temperature: {agent.temperature}")
        print(f"  Max Tokens: {agent.max_tokens}")
        print(f"  Cache Enabled: {'Yes' if agent.cache else 'No'}")
        print(f"  Tags: {', '.join(agent.tags) if agent.tags else 'None'}")
        print(f"  Research Domain: {'Yes' if agent.is_research_domain else 'No'}")
    
    # Get a database session
    try:
        session = app_config.get_db_session()
        print(f"\nSuccessfully connected to database: {app_config.db_config.database}")
    except Exception as e:
        print(f"\nCouldn't connect to database: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 4. Custom Startup Task Example
cat > examples/04_custom_startup.py << 'EOF'
"""
Custom Startup Task Example

This example demonstrates how to create and use custom startup tasks
with auto-discovery, ordering, and configuration.
"""
import asyncio
import logging
from src import engine
from src.core.startup import StartupTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define a custom startup task
class DatabaseInitializationTask(StartupTask):
    """Custom startup task to initialize the database."""
    
    # Run after configuration is loaded (order 10-20)
    order = 30
    
    def execute(self) -> None:
        """Execute the database initialization."""
        logger.info("Initializing database...")
        
        # Get configuration parameters from task config
        schema_name = self._config.get('schema', 'public')
        create_tables = self._config.get('create_tables', True)
        
        logger.info(f"Using schema: {schema_name}")
        logger.info(f"Create tables: {create_tables}")
        
        # In a real app, you'd create database tables here
        # ...

# Define another custom startup task
class ModelInitializationTask(StartupTask):
    """Custom startup task to initialize AI models."""
    
    # Run after database initialization
    order = 40
    
    def execute(self) -> None:
        """Execute the model initialization."""
        logger.info("Initializing AI models...")
        
        # Get configuration parameters
        default_model = self._config.get('default_model', 'default')
        preload = self._config.get('preload', False)
        
        logger.info(f"Default model: {default_model}")
        logger.info(f"Preload models: {preload}")
        
        # In a real app, you'd initialize models here
        # ...

async def main():
    # Initialize and start the engine
    # The engine will auto-discover our tasks
    engine.initialize()
    engine.start()
    
    # Print information about discovered tasks
    print("\nStartup Tasks:")
    for task_name, task in engine._startup_task_executor._tasks.items():
        status = "Enabled" if task.enabled else "Disabled"
        print(f"- {task_name} (Order: {task.order}, Status: {status})")
    
    # Print startup task configuration
    from src.config.yaml_config import YamlConfig
    config = engine.resolve(YamlConfig)
    
    print("\nStartup Task Configuration:")
    startup_tasks_config = config.get('startup_tasks', {})
    for task_name, task_config in startup_tasks_config.items():
        print(f"\n{task_name}:")
        for key, value in task_config.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 5. Database Operations Example
cat > examples/05_database_operations.py << 'EOF'
"""
Database Operations Example

This example demonstrates how to perform more advanced
database operations using the repository pattern with entities.
"""
import asyncio
import uuid
from typing import Optional, List, Protocol
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository
from src.data.specification import Specification

# Define entities
class User(BaseEntity):
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)

class Post(BaseEntity):
    __tablename__ = "posts"
    
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    published: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

# Define repository interfaces
class IUserRepository(IRepository[User], Protocol):
    async def find_by_username(self, username: str) -> Optional[User]: ...
    async def find_by_email(self, email: str) -> Optional[User]: ...

class IPostRepository(IRepository[Post], Protocol):
    async def find_by_user_id(self, user_id: str) -> List[Post]: ...
    async def find_published(self) -> List[Post]: ...
    async def publish(self, post: Post) -> Post: ...

# Define specifications
class UserByUsernameSpecification(Specification[User]):
    def __init__(self, username: str):
        self.username = username
    
    def to_expression(self):
        return User.username == self.username

class UserByEmailSpecification(Specification[User]):
    def __init__(self, email: str):
        self.email = email
    
    def to_expression(self):
        return User.email == self.email

class PostByUserIdSpecification(Specification[Post]):
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def to_expression(self):
        return Post.user_id == self.user_id

class PublishedPostSpecification(Specification[Post]):
    def to_expression(self):
        return Post.published == True

async def main():
    # Initialize and start the engine
    engine.initialize()
    engine.start()
    
    # Resolve repositories
    user_repository = engine.resolve(IUserRepository)
    post_repository = engine.resolve(IPostRepository)
    
    print("Database Operations Example:")
    print("===========================")
    
    # Create a user entity
    user = User(
        id=str(uuid.uuid4()),
        username="johndoe",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe"
    )
    
    # Save the user
    created_user = await user_repository.create(user)
    print(f"\nCreated user: {created_user.first_name} {created_user.last_name} ({created_user.username})")
    
    # Create post entities
    post1 = Post(
        id=str(uuid.uuid4()),
        title="First Post",
        content="This is my first post!",
        published=False,
        user_id=created_user.id
    )
    
    post2 = Post(
        title="Second Post",
        content="This is my second post!",
        published=False,
        user_id=created_user.id
    )
    
    # Save posts
    created_post1 = await post_repository.create(post1)
    created_post2 = await post_repository.create(post2)
    
    print(f"\nCreated posts: {created_post1.title}, {created_post2.title}")
    
    # Publish a post
    created_post1.published = True
    published_post = await post_repository.update(created_post1)
    print(f"\nPublished post: {published_post.title}")
    
    # Find posts by user
    user_posts = await post_repository.find(PostByUserIdSpecification(created_user.id))
    print(f"\nUser has {len(user_posts)} posts:")
    for post in user_posts:
        status = "Published" if post.published else "Draft"
        print(f"- {post.title} ({status})")
    
    # Find published posts
    published_posts = await post_repository.find(PublishedPostSpecification())
    print(f"\nPublished posts: {len(published_posts)}")
    
    # Find user by username
    found_user = await user_repository.find_one(UserByUsernameSpecification("johndoe"))
    if found_user:
        print(f"\nFound user by username: {found_user.first_name} {found_user.last_name}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 6. Auto-discovery Example
cat > examples/06_autodiscovery.py << 'EOF'
"""
Auto-discovery Example

This example demonstrates how the engine auto-discovers
startup tasks and other components.
"""
import asyncio
import logging
from src import engine
from src.core.startup import StartupTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define a new startup task that will be auto-discovered
class ExampleAutoDiscoveredTask(StartupTask):
    """Example task that will be auto-discovered."""
    
    order = 100  # Run late in the sequence
    enabled = True
    
    def execute(self) -> None:
        """Execute the task."""
        logger.info("Auto-discovered task executed!")
        logger.info(f"Task configuration: {self._config}")

async def main():
    # Let the engine initialize without manually registering any tasks
    engine.initialize()
    engine.start()
    
    print("\nAuto-discovered Startup Tasks:")
    for task_name, task in engine._startup_task_executor._tasks.items():
        status = "Enabled" if task.enabled else "Disabled"
        print(f"- {task_name} (Order: {task.order}, Status: {status})")
    
    print("\nLoaded Configuration:")
    try:
        from src.config.yaml_config import YamlConfig
        config = engine.resolve(YamlConfig)
        print(f"App Default Model Provider: {config.get('app.default_model_provider')}")
        print(f"Database Host: {config.get('database.host')}")
        
        # Print number of agents
        agents = config.get('app.agents', {})
        print(f"Number of configured agents: {len(agents)}")
    except Exception as e:
        print(f"Configuration not loaded: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 7. Multi-configuration Example
cat > examples/07_multi_config.py << 'EOF'
"""
Multi-configuration Example

This example demonstrates how to work with multiple
configuration sources - YAML and environment variables.
"""
import asyncio
import os
from src import engine
from src.core.startup import StartupTask
from src.config.yaml_config import YamlConfig
from src.config.environment import Environment

# Define a startup task to load environment variables
class EnvironmentStartupTask(StartupTask):
    """Startup task to load environment variables."""
    
    # Run before configuration
    order = 5
    
    def execute(self) -> None:
        # Set some environment variables for demonstration
        os.environ["HERPAI_DB_HOST"] = "env-db-host"
        os.environ["HERPAI_DB_PORT"] = "5433"
        os.environ["HERPAI_API_KEY"] = "env-api-key-123"
        os.environ["HERPAI_DEBUG"] = "true"

async def main():
    # Initialize and start the engine
    engine.initialize()
    engine.start()
    
    # Access YAML configuration
    yaml_config = engine.resolve(YamlConfig)
    
    print("Multi-configuration Example:")
    print("===========================")
    
    print("\nYAML Configuration:")
    print(f"Database Host (YAML): {yaml_config.get('database.host')}")
    print(f"Database Port (YAML): {yaml_config.get('database.port')}")
    
    print("\nEnvironment Variables:")
    print(f"Database Host (ENV): {Environment.get('HERPAI_DB_HOST')}")
    print(f"Database Port (ENV): {Environment.get('HERPAI_DB_PORT')}")
    print(f"API Key (ENV): {Environment.get('HERPAI_API_KEY')}")
    print(f"Debug Mode (ENV): {Environment.get_bool('HERPAI_DEBUG')}")
    
    print("\nMerged Configuration (Environment takes precedence):")
    db_host = Environment.get('HERPAI_DB_HOST') or yaml_config.get('database.host')
    db_port = Environment.get_int('HERPAI_DB_PORT') or yaml_config.get('database.port')
    print(f"Database Host (Merged): {db_host}")
    print(f"Database Port (Merged): {db_port}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Create a README for the examples directory
cat > examples/README.md << 'EOF'
# HerpAI-Lib Examples

This directory contains examples demonstrating different features of HerpAI-Lib.

## Running Examples

To run an example, make sure you have HerpAI-Lib installed, then execute the Python file:

```bash
python examples/01_basic_todo.py
```

Most examples require a `config.yaml` file in the current directory. You can use the provided sample configuration.

## Available Examples

| Example | Description |
|---------|-------------|
| [01_basic_todo.py](01_basic_todo.py) | Basic repository pattern with a Todo entity |
| [02_yaml_config.py](02_yaml_config.py) | Working with YAML configuration and dotted access |
| [03_app_config.py](03_app_config.py) | Using strongly-typed dataclass configuration |
| [04_custom_startup.py](04_custom_startup.py) | Creating custom startup tasks with ordering |
| [05_database_operations.py](05_database_operations.py) | Advanced database operations with repositories |
| [06_autodiscovery.py](06_autodiscovery.py) | Auto-discovery of startup tasks and components |
| [07_multi_config.py](07_multi_config.py) | Working with multiple configuration sources |
EOF

echo "Created 7 updated example files following proper entity and DI patterns."