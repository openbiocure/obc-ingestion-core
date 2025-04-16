[OpenBioCure_CoreLib on PyPI](https://pypi.org/project/openbiocure-corelib/)

# OpenBioCure_CoreLib

[![Makefile CI](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml)

**OpenBioCure_CoreLib** is the foundational core library for the [HerpAI](https://github.com/openbiocure/HerpAI) platform. It provides shared infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern used across HerpAI agents and services.

## 📋 Documentation

This section provides detailed documentation on the core components and usage of `OpenBioCure_CoreLib`, informed by the library's source code.

### Core Concepts Explained

*   **Dependency Injection (DI) Engine (`engine: IEngine`)**:
    *   **Source**: `openbiocure_corelib.core.engine.Engine`
    *   **Role**: The central singleton orchestrator managing the application's lifecycle and services. Accessed via `engine.current()`.
    *   **Lifecycle**:
        *   `initialize()`: Sets up the engine and registers core services. Call this first.
        *   `register_module(module_path)`: Scans a module path for discoverable components (like `StartupTask`s).
        *   `add_startup_task(task)`: Manually adds a `StartupTask`.
        *   `start()`: Executes registered `StartupTask`s in order.
        *   `stop()`: Cleans up resources, potentially calling `cleanup()` on tasks.
    *   **Service Management**:
        *   `register(interface_type, implementation)`: Registers services (delegates to `ServiceCollection`).
        *   `resolve(Type[T])`: Retrieves a registered service instance.
        *   `create_scope()`: Creates an `IServiceScope` for managing scoped service lifetimes.
*   **Service Collection (`ServiceCollection`)**:
    *   **Source**: `openbiocure_corelib.core.service_collection.ServiceCollection`
    *   **Role**: Internal registry used by the `Engine` to manage service definitions and lifetimes.
    *   **Methods**: `add_singleton`, `add_scoped`, `add_transient` define how services are instantiated and cached. `get_service` retrieves definitions.
*   **Service Scopes (`IServiceScope`)**:
    *   **Source**: `openbiocure_corelib.core.service_scope.ServiceScope`
    *   **Role**: Manages the lifetime of 'scoped' services. Created via `engine.create_scope()`.
    *   **Methods**: `resolve(Type[T])` retrieves services within the scope. `dispose()` cleans up scoped instances.
*   **Repository Pattern (`IRepository[T]`, `Repository[T]`)**:
    *   **Source**: `openbiocure_corelib.data.repository`
    *   **Role**: Abstracts data access logic for specific entity types (`T`). Promotes testability and separation of concerns. Requires an `AsyncSession` (usually from `DbContext`).
    *   **Key Methods**:
        *   `create(entity | **kwargs)`: Adds a new entity.
        *   `get(id)`: Retrieves an entity by its primary key.
        *   `update(id | entity, **kwargs)`: Modifies an existing entity.
        *   `delete(id)`: Removes an entity by its primary key.
        *   `find(spec: ISpecification[T])`: Retrieves a list of entities matching the specification criteria.
*   **Specification Pattern (`ISpecification[T]`, `Specification[T]`)**:
    *   **Source**: `openbiocure_corelib.data.specification`
    *   **Role**: Encapsulates query logic in reusable objects. Used with `Repository.find()`.
    *   **Key Methods**:
        *   `to_expression()`: Translates the specification into a SQLAlchemy query expression (e.g., `User.name == ' Cline'`).
        *   `is_satisfied_by(entity)`: (Less common for DB queries) Checks if an in-memory entity matches.
    *   **Composition**: Combine specifications using `and_()` and `or_()` (or `&` and `|` operators via `AndSpecification`, `OrSpecification`).
*   **Configuration Management**:
    *   **Sources**: `openbiocure_corelib.config.yaml_config`, `openbiocure_corelib.config.app_config`, `openbiocure_corelib.config.dataclass_config`, `openbiocure_corelib.config.environment`
    *   **Role**: Provides ways to load and access application settings.
    *   **Approaches**:
        *   `YamlConfig`: Flexible, dictionary-based access to YAML files. Use `load()` and `get('dotted.key')`. Registered as a singleton by default.
        *   `AppConfig` / `DatabaseConfig` / `AgentConfig`: Strongly-typed dataclasses (defined in both `app_config.py` and `dataclass_config.py` - *Note: potential duplication*). Provides validation and type hints. Use `load()` and access attributes directly. Often used alongside `YamlConfig`.
        *   `Environment`: Helper class to read OS environment variables (`get`, `get_bool`, `get_int`).
    *   **Loading**: Typically handled by `ConfigurationStartupTask`.
*   **Startup Tasks (`StartupTask`)**:
    *   **Source**: `openbiocure_corelib.core.startup_task.StartupTask`
    *   **Role**: Defines ordered, asynchronous operations to run during application initialization (`engine.start()`).
    *   **Implementation**: Inherit `StartupTask`, override `async execute()`, set `order` (lower runs first). Can optionally implement `configure(config)` and `async cleanup()`.
    *   **Execution**: Managed by `StartupTaskExecutor`. Tasks can be added manually (`engine.add_startup_task`) or auto-discovered.
    *   **Built-in Tasks**: `ConfigurationStartupTask`, `DatabaseSchemaStartupTask`.
*   **Auto-discovery (`TypeFinder`)**:
    *   **Source**: `openbiocure_corelib.core.type_finder.TypeFinder`
    *   **Role**: Scans specified Python modules or the entire environment to find classes implementing specific base classes or protocols (e.g., `StartupTask`, `IRepository`). Used by the `Engine` during initialization and registration phases.
    *   **Methods**: `find_classes_of_type`, `find_generic_implementations`.
*   **Database Context (`IDbContext`, `DbContext`)**:
    *   **Source**: `openbiocure_corelib.data.db_context.DbContext`
    *   **Role**: Manages the database connection (via SQLAlchemy `create_async_engine`) and provides access to `AsyncSession` instances for repository operations.
    *   **Initialization**: Requires a connection string or `DatabaseConfig`. `initialize()` sets up the engine and optionally creates the schema (`create_schema`). `close()` disposes of the engine.
    *   **Usage**: Typically registered as a singleton. Repositories resolve `AsyncSession` from it via `session()`. `execute()` allows running raw SQL or SQLAlchemy core statements.

### Key Modules and Classes (Detailed)

*   **`openbiocure_corelib.core`**: The heart of the application framework.
    *   `Engine`: Central DI container and lifecycle manager.
    *   `IEngine`: Protocol defining the engine's public interface.
    *   `ServiceCollection`: Internal registry for service definitions (singleton, scoped, transient).
    *   `IServiceScope`: Protocol for managing scoped service instances.
    *   `ServiceScope`: Default implementation of `IServiceScope`.
    *   `StartupTask`: Base class for defining initialization steps.
    *   `StartupTaskExecutor`: Discovers, orders, and executes `StartupTask`s.
    *   `TypeFinder`: Implements auto-discovery of classes based on type/protocol.
    *   `ITypeFinder`: Protocol for type discovery.
    *   `ConfigurationStartupTask`: Built-in task to load configuration using `YamlConfig`.
    *   `Singleton`: (Potentially a helper or metaclass for singletons, usage context needed).
*   **`openbiocure_corelib.config`**: Configuration loading and access.
    *   `YamlConfig`: Loads settings from YAML files, provides dictionary-like access (`get`).
    *   `AppConfig`, `DatabaseConfig`, `AgentConfig`: Dataclasses for strongly-typed configuration (defined in both `app_config.py` and `dataclass_config.py`). Methods like `load`, `from_dict`, `connection_string`.
    *   `Environment`: Static methods to access OS environment variables.
    *   `Settings`: Class for potentially managing persistent settings (e.g., saving to a file - `load`, `get`, `set`, `save`). Its exact role might need clarification from usage.
    *   `ConfigError`: Custom exception for configuration issues.
*   **`openbiocure_corelib.data`**: Data access layer components.
    *   `DbContext`: Manages SQLAlchemy async engine and sessions.
    *   `IDbContext`: Protocol defining the DbContext interface.
    *   `BaseEntity`: Base class for SQLAlchemy declarative models.
    *   `IRepository[T]`: Protocol defining generic repository operations (CRUD + find).
    *   `Repository[T]`: Generic implementation of `IRepository` using `AsyncSession`.
    *   `ISpecification[T]`: Protocol for query specifications.
    *   `Specification[T]`: Base implementation for specifications, including composition methods (`and_`, `or_`).
    *   `AndSpecification`, `OrSpecification`: Concrete composite specifications.
    *   `DatabaseSchemaStartupTask`: Built-in task to initialize the database schema via `DbContext.create_schema()`.
*   **`openbiocure_corelib.infrastructure`**: (Currently sparse) Intended for cross-cutting concerns like caching, event handling, logging wrappers.

### Usage Examples

Refer to the [Examples](#-examples) section and the `examples/` directory for practical demonstrations of these concepts. The examples showcase how to combine these components for common tasks.

### Configuration Details

*   **Primary Method**: Use a `config.yaml` file (or multiple) loaded by `ConfigurationStartupTask` into the `YamlConfig` singleton. Access via `engine.resolve(YamlConfig).get('some.key')`.
*   **Typed Configuration**: Define dataclasses inheriting from `AppConfig` (or standalone like `DatabaseConfig`). Load them from the dictionary provided by `YamlConfig` or directly from a file using their `load` or `from_dict` methods. Access via `engine.resolve(YourAppConfig)` if registered, or manage instances manually.
*   **Database Setup**: Configure database connection details under a `database` key in YAML (e.g., `type`, `path`, `host`, `port`, `username`, `password`) used by `DbContext` or `DatabaseConfig`. The `DbContext` can use either a direct connection string or a `DatabaseConfig` object.
*   **Environment Overrides**: Use `Environment.getX` for settings that might change between deployment environments (e.g., API keys, debug flags).

```yaml
# Example config.yaml
database:
  type: sqlite # e.g., sqlite, postgresql
  path: "db/app.db" # For sqlite
  # host: localhost # For others
  # port: 5432
  # username: user
  # password: pass
  # database_name: myapp
  echo: false # Log SQL statements?

app:
  name: "My CoreLib App"
  default_model_provider: "some_provider"
  # Other app-specific settings

logging:
  level: INFO # e.g., DEBUG, INFO, WARNING, ERROR

# Optional: Configuration for specific startup tasks
# MyCustomTask:
#   setting1: value1
```

### Extending the Library

*   **Custom Repositories**:
    1.  Define your SQLAlchemy model inheriting `BaseEntity`.
    2.  Define an interface inheriting `IRepository[YourEntity]`.
    3.  Implement the interface inheriting `Repository[YourEntity]`.
    4.  Register with the engine: `engine.register(IYourRepository, YourRepository)`. Auto-discovery might handle this if `YourRepository` is in a scanned module.
*   **Custom Startup Tasks**:
    1.  Create a class inheriting `StartupTask`.
    2.  Set a unique `order` attribute (integer).
    3.  Implement `async def execute(self) -> None:`.
    4.  Optionally implement `configure(self, config)` and `async cleanup(self) -> None:`.
    5.  Ensure the task is discoverable (in a scanned module) or add it manually via `engine.add_startup_task()`.
*   **Custom Services**:
    1.  Define your service class and optionally an interface (protocol).
    2.  Register it using `engine.services.add_singleton(IMyService, MyService)`, `add_scoped`, or `add_transient`.

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
