[OpenBioCure_CoreLib on PyPI](https://pypi.org/project/openbiocure-corelib/)

# OpenBioCure_CoreLib

[![Makefile CI](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml)

**OpenBioCure_CoreLib** is the foundational core library for the [HerpAI](https://github.com/openbiocure/HerpAI) platform. It provides shared infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern used across HerpAI agents and services.

## 📋 Documentation

- See the changelog at the bottom of this file for recent updates.

## 💬 Join the Community

Come chat with us on Discord: [HerpAI Discord Server](https://discord.gg/72dWs7J9)

## 📦 Features

- 🧠 **Dependency Injection** - Service registration and resolution
- 🔄 **Repository Pattern** - Type-safe entity operations
- 🔍 **Specification Pattern** - Fluent query filtering
- 🧵 **Async Support** - Full async/await patterns
- 📝 **Type Safety** - Generic interfaces with Python typing
- ⚙️ **Configuration Management** - YAML with dataclass validation and OOP interface
- 🚀 **Auto-discovery Startup System** - Ordered initialization with configuration
- 🪵 **Structured Logging** - Consistent format across components

## 🛠️ Installation

```bash
pip install openbiocure-corelib
```

Or install from GitHub:

```bash
pip install git+https://github.com/openbiocure/HerpAI-Lib.git
```

For development:

```bash
git clone https://github.com/openbiocure/HerpAI-Lib.git
cd HerpAI-Lib
pip install -e .
```

## ⚡ Quick Example

```python
import asyncio
from openbiocure_corelib import engine
from examples.domain.todo_entity import Todo
from examples.repository.todo_repository import ITodoRepository, CompletedTodoSpecification

async def main():
    # Initialize and start the engine
    engine.initialize()
    await engine.start()

    # Resolve the todo repository
    todo_repository = engine.resolve(ITodoRepository)

    # Create a Todo entity
    todo = Todo(
        title="Learn OpenBioCure_CoreLib",
        description="Implement repository pattern with dependency injection",
        completed=False
    )
    created_todo = await todo_repository.create(todo)
    print(f"Created Todo: {created_todo.title}")

    # Mark as completed
    created_todo.completed = True
    await todo_repository.update(created_todo)

    # Query completed todos
    completed_todos = await todo_repository.find(CompletedTodoSpecification())
    print(f"Completed todos: {len(completed_todos)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 Examples

| Example | Description |
|---------|-------------|
| [01_basic_todo.py](examples/01_basic_todo.py) | Basic repository pattern with a Todo entity |
| [02_yaml_config.py](examples/02_yaml_config.py) | Working with YAML configuration and dotted access |
| [03_app_config.py](examples/03_app_config.py) | Using strongly-typed dataclass configuration |
| [04_custom_startup.py](examples/04_custom_startup.py) | Creating custom startup tasks with ordering |
| [05_database_operations.py](examples/05_database_operations.py) | Advanced database operations with repositories |
| [06_autodiscovery.py](examples/06_autodiscovery.py) | Auto-discovery of startup tasks and components |
| [07_multi_config.py](examples/07_multi_config.py) | Working with multiple configuration sources |

## 📁 Library Structure

```
openbiocure_corelib/
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
│   └── exceptions.py         # Core exceptions
│
├── data/                     # Data access
│   ├── entity.py             # Base entity
│   ├── repository.py         # Repository pattern
│   ├── specification.py      # Specification pattern
│   └── db_context.py         # Database context
```

## 🧪 Requirements

- Python 3.9+
- SQLAlchemy
- PyYAML
- aiosqlite
- dataclasses (built-in for Python 3.9+)

## 📝 License

This library is released under the MIT License as part of the OpenBioCure initiative.

---

# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0).

## [0.2.1] - 2025-04-05

### Changed
- Renamed the library to `openbiocure_corelib`
- Updated project metadata and package name accordingly
- Bumped version to 0.2.1

## [Unreleased]

### Added
- Test database directory fixture (`test_db_dir`) to create temporary directory for test database files
- Support for direct database connection string configuration
- Proper cleanup in `initialized_engine` fixture
- Comprehensive test cases for error handling and edge cases in Repository
- CI environment detection to use in-memory databases in CI

### Changed
- Updated test configuration to use temporary database path
- Improved database context startup task to handle both connection string and individual parameters
- Modified `Engine.current()` test to properly await engine start
- Updated `Repository.update` method to handle both string IDs and entity objects
- Enhanced validation in TestEntity to properly raise SQLAlchemyError for null name
- Updated Engine.stop() method to properly clear ServiceCollection without using non-existent clear() method
- Modified test configuration to use in-memory databases in CI environments

### Fixed
- Database path issues in CI environment
- SQLite database file access in tests
- Immutable fields handling in Repository updates
- Test startup tasks to utilize async execute methods
- RuntimeError: 'Engine not started' by ensuring proper engine initialization
- AttributeError in Engine.stop() method when clearing ServiceCollection
- SQLite database access errors in CI by using in-memory databases

### Improved
- Test coverage for repository operations
- Error handling in CRUD operations
- Edge case handling in find operations
- Documentation about the async startup process
