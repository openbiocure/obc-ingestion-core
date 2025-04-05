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

## 🆕 What's New in 3.1.0

- Core symbols like `IRepository`, `Repository`, `BaseEntity`, `Specification`, `YamlConfig`, `Environment`, `StartupTask`, and `AppConfig` are now exposed directly from the root package.
- This simplifies imports. For example:

```python
from openbiocure_corelib import IRepository, Repository, BaseEntity, Specification, YamlConfig, Environment, StartupTask, AppConfig
```

- Created a dedicated release branch `release-3.1.0` containing these changes.
- See the [Changelog](#changelog) for full details.

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

## ⚡ Quick Examples

### Basic Todo Repository

```python
import asyncio
from openbiocure_corelib import engine
from examples.domain.todo_entity import Todo
from examples.repository.todo_repository import ITodoRepository, CompletedTodoSpecification

async def main():
    engine.initialize()
    await engine.start()

    todo_repo = engine.resolve(ITodoRepository)

    todo = Todo(title="Learn OpenBioCure_CoreLib", description="Use DI and repository", completed=False)
    created = await todo_repo.create(todo)

    created.completed = True
    await todo_repo.update(created)

    completed_todos = await todo_repo.find(CompletedTodoSpecification())
    print(f"Completed todos: {len(completed_todos)}")

asyncio.run(main())
```

### Accessing YAML Configuration

```python
from openbiocure_corelib import engine, YamlConfig

engine.initialize()
config = engine.resolve(YamlConfig)

print(config.get('database.host'))
print(config.get('app.default_model_provider'))
```

### Custom Startup Task

```python
from openbiocure_corelib import StartupTask

class MyStartupTask(StartupTask):
    order = 50

    async def execute(self):
        print("Running my startup task!")
```

### Advanced Database Queries with Specifications

```python
from openbiocure_corelib import Specification

class UserByUsernameSpec(Specification):
    def __init__(self, username):
        self.username = username

    def to_expression(self):
        from myapp.models import User
        return User.username == self.username

# Usage:
user_repo = engine.resolve(IUserRepository)
user = await user_repo.find_one(UserByUsernameSpec("johndoe"))
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
├── config/
│   ├── app_config.py
│   ├── dataclass_config.py
│   ├── environment.py
│   ├── settings.py
│   └── yaml_config.py
├── core/
│   ├── configuration_startup_task.py
│   ├── engine.py
│   ├── interfaces.py
│   ├── service_collection.py
│   ├── service_scope.py
│   ├── singleton.py
│   ├── startup_task_executor.py
│   ├── startup_task.py
│   └── type_finder.py
├── data/
│   ├── db_context_startup_task.py
│   ├── db_context.py
│   ├── entity.py
│   ├── repository.py
│   └── specification.py
├── domain/
├── infrastructure/
│   ├── caching/
│   ├── events/
│   └── logging/
└── utils/
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
