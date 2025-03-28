# HerpAI-Lib

[![Makefile CI](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml)

**HerpAI-Lib** is the foundational core library for the [HerpAI](https://github.com/openbiocure/HerpAI) platform. It provides shared infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern used across HerpAI agents and services.

## 💬 Join the Community

Come chat with us on Discord: [HerpAI Discord Server](https://discord.com/channels/1354737744638771220/1354737744638771223)

---

## 📦 Features

- 🧠 **Dependency Injection** - Service registration and resolution
- 🔄 **Repository Pattern** - Type-safe entity operations
- 🔍 **Specification Pattern** - Fluent query filtering
- 🧵 **Async Support** - Full async/await patterns
- 📝 **Type Safety** - Generic interfaces with Python typing
- ⚙️ **Configuration Management** - YAML with dataclass validation and OOP interface
- 🚀 **Startup Tasks** - Initialization sequence control
- 🪵 **Structured Logging** - Consistent format across components

---

## 🛠️ Installation

```bash
pip install git+https://github.com/openbiocure/HerpAI-Lib.git
```

Or for development:

```bash
git clone https://github.com/openbiocure/HerpAI-Lib.git
cd HerpAI-Lib
pip install -e .
```

---

## 🚀 Getting Started

### Basic Usage

```python
from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository

# Initialize the library
engine.initialize()
engine.start()

# Resolve your repositories
repository = engine.resolve(IRepository[YourEntity])

# Use the repository
entity = await repository.create(name="Example")
```

### Configuration with Dataclasses

HerpAI-Lib supports strongly-typed configuration using dataclasses:

```python
from src import engine
from src.core.app_config_startup import AppConfigStartupTask
from src.config.dataclass_config import AppConfig

# Add configuration startup task
engine.add_startup_task(AppConfigStartupTask("config.yaml"))

# Initialize the engine
engine.initialize()
engine.start()

# Get the configuration
config = AppConfig.get_instance()

# Access agent configuration
virology_agent = config.get_agent("virology")
print(f"Model: {virology_agent.model}")
print(f"Temperature: {virology_agent.temperature}")

# Get database session
db_session = config.get_db_session()
```

### Custom Startup Tasks

You can create custom startup tasks to run during initialization:

```python
from src.core.startup import StartupTask

class DatabaseSetupStartupTask(StartupTask):
    def execute(self) -> None:
        print("Setting up database...")
        # Your initialization code here

# Add it to the engine
engine.add_startup_task(DatabaseSetupStartupTask())
```

---

## 📋 Examples

Explore the following examples to learn how to use HerpAI-Lib:

| Example | Description |
|---------|-------------|
| [01_basic_todo.py](examples/01_basic_todo.py) | Basic repository pattern with a Todo entity |
| [02_yaml_config.py](examples/02_yaml_config.py) | Working with YAML configuration and dotted access |
| [03_app_config.py](examples/03_app_config.py) | Using strongly-typed dataclass configuration |
| [04_custom_startup.py](examples/04_custom_startup.py) | Creating custom startup tasks with ordering |
| [05_database_operations.py](examples/05_database_operations.py) | Advanced database operations with repositories |
| [06_autodiscovery.py](examples/06_autodiscovery.py) | Auto-discovery of startup tasks and components |
| [07_multi_config.py](examples/07_multi_config.py) | Working with multiple configuration sources |

For more details on each example, see the [examples README](examples/README.md).

### Basic Todo Example

A simple example of using the repository pattern with entities:

```python
# See examples/todo_example.py
import asyncio
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

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
    engine.initialize()
    engine.start()
    
    # Resolve what we need
    todo_repository = engine.resolve(ITodoRepository)
    
    # Use the repository
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

if __name__ == "__main__":
    asyncio.run(main())
```

### Configured Example with YAML

An example showing configuration with YAML and startup tasks:

```python
# See examples/configured_todo_example.py
import asyncio
from src import engine
from src.core.startup import ConfigurationStartupTask, StartupTask
from src.config.yaml_config import YamlConfig

# Define a custom startup task
class DatabaseSetupStartupTask(StartupTask):
    def execute(self) -> None:
        print("Preparing database...")
        # This would typically create tables, run migrations, etc.

async def main():
    # Add startup tasks
    engine.add_startup_task(ConfigurationStartupTask("config.yaml"))
    engine.add_startup_task(DatabaseSetupStartupTask())
    
    # Initialize and start the engine
    engine.initialize()
    engine.start()
    
    # Access configuration
    config = YamlConfig.get_instance()
    db_config = config.get('database', {})
    print(f"Connected to database: {db_config.get('database')} on {db_config.get('host')}")
    
    # Print some agent configurations
    agents = config.get_agent_configs()
    print(f"Configured agents: {', '.join(agents.keys())}")
    
    # Continue with repository pattern as in basic example...

if __name__ == "__main__":
    asyncio.run(main())
```

### Using AppConfig with Full Type Safety

An example showing how to use the strongly-typed configuration classes:

```python
# See examples/app_config_example.py
import asyncio
from src import engine
from src.core.app_config_startup import AppConfigStartupTask
from src.config.dataclass_config import AppConfig

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
    
    # Get a database session
    try:
        session = app_config.get_db_session()
        print(f"\nConnected to database: {app_config.db_config.database}")
    except Exception as e:
        print(f"Database connection error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📁 Library Structure

```
src/
├── config/                   # Configuration management
│   ├── settings.py           # Settings management
│   ├── environment.py        # Environment variables
│   ├── yaml_config.py        # Basic YAML configuration
│   └── dataclass_config.py   # Typed dataclass configuration
│
├── core/                     # Core engine components
│   ├── engine.py             # DI container and engine
│   ├── dependency.py         # Dependency injection
│   ├── startup.py            # Startup tasks
│   ├── app_config_startup.py # AppConfig startup task
│   └── exceptions.py         # Core exceptions
│
├── data/                     # Data access
│   ├── entity.py             # Base entity
│   ├── repository.py         # Repository pattern
│   ├── specification.py      # Specification pattern
│   └── db_context.py         # Database context
│
├── domain/                   # Domain layer
│   ├── events.py             # Domain events
│   └── services.py           # Service layer
│
├── infrastructure/           # Infrastructure components
│   ├── caching/              # Caching components
│   ├── events/               # Event system
│   └── logging/              # Logging system
│
└── utils/                    # Utility functions
    ├── helpers.py            # General helpers
    └── async_utils.py        # Async utilities
```

---

## 🧪 Requirements

- Python 3.9+
- SQLAlchemy
- PyYAML
- aiosqlite
- dataclasses (built-in for Python 3.9+)

---

## 📝 License

This library is released under the MIT License as part of the OpenBioCure initiative.