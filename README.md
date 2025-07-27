# 🐍 OpenBioCure Ingestion Core Library

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=for-the-badge&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Makefile CI](https://github.com/openbiocure/obc-ingestion-core/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/obc-ingestion-core/actions/workflows/makefile.yml)


**OpenBioCure Ingestion Core** is the foundational library for data ingestion and processing in the OpenBioCure platform. It provides enterprise-grade infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern for building robust data ingestion workflows.

[![PyPI version](https://badge.fury.io/py/obc-ingestion-core.svg)](https://badge.fury.io/py/obc-ingestion-core)
[![Downloads](https://img.shields.io/pypi/dm/obc-ingestion-core.svg)](https://pypi.org/project/obc-ingestion-core/)
[![GitHub stars](https://img.shields.io/github/stars/openbiocure/obc-ingestion-core.svg?style=social&label=Star)](https://github.com/openbiocure/obc-ingestion-core)
[![GitHub forks](https://img.shields.io/github/forks/openbiocure/obc-ingestion-core.svg?style=social&label=Fork)](https://github.com/openbiocure/obc-ingestion-core)

## 🛠️ Tech Stack

[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)
[![PyYAML](https://img.shields.io/badge/PyYAML-6.0+-green.svg?style=for-the-badge&logo=yaml&logoColor=white)](https://pyyaml.org/)
[![aiosqlite](https://img.shields.io/badge/aiosqlite-0.17+-blue.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://aiosqlite.readthedocs.io/)
[![asyncio](https://img.shields.io/badge/asyncio-Native-orange.svg?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/asyncio.html)

## 🚀 Features

- 🧠 **Dependency Injection** - Service registration and resolution
- 🔄 **Repository Pattern** - Type-safe entity operations with SQLAlchemy
- 🔍 **Specification Pattern** - Fluent query filtering and composition
- 🧵 **Async Support** - Full async/await patterns throughout
- 📝 **Type Safety** - Generic interfaces with Python typing
- ⚙️ **Configuration Management** - YAML with dataclass validation
- 🚀 **Auto-discovery Startup System** - Ordered initialization with configuration
- 🪵 **Structured Logging** - Consistent format across components
- 🔧 **Database Integration** - SQLAlchemy async support with schema management

## 🛠️ Installation

```bash
pip install obc-connectors-core
```

Or install from GitHub:

```bash
pip install git+https://github.com/openbiocure/obc-connectors-core.git
```

For development:

```bash
git clone https://github.com/openbiocure//obc-connectors-core.git
cd obc-ingestion-core
pip install -e .
```

## ⚡ Quick Start

### Basic Usage

```python
import asyncio
from obc_ingestion_core import engine, IRepository, Repository, BaseEntity

# Initialize and start the engine
engine.initialize()
await engine.start()

# Resolve services
my_repo = engine.resolve(IRepository[MyEntity])

# Use the repository
entity = await my_repo.create(title="My Entity")
entities = await my_repo.find(MySpecification())
```

### Configuration

```python
from obc_ingestion_core import YamlConfig, AppConfig

# Access YAML configuration
config = engine.resolve(YamlConfig)
db_host = config.get('database.host')

# Access typed configuration
app_config = engine.resolve(AppConfig)
model_provider = app_config.default_model_provider
```

## 📋 Core Concepts

### Dependency Injection Engine

The central orchestrator managing application lifecycle and services:

```python
from obc_ingestion_core import engine

# Initialize the engine
engine.initialize()

# Register services
engine.register(IMyService, MyService)

# Resolve services
my_service = engine.resolve(IMyService)

# Start the application
await engine.start()
```

### Repository Pattern

Type-safe data access with SQLAlchemy integration:

```python
from obc_ingestion_core import IRepository, Repository, BaseEntity

class Todo(BaseEntity):
    __tablename__ = "todos"
    title: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)

class ITodoRepository(IRepository[Todo], Protocol):
    pass

class TodoRepository(Repository[Todo]):
    pass

# Auto-registered by engine
todo_repo = engine.resolve(ITodoRepository)
todo = await todo_repo.create(title="Learn CoreLib", completed=False)
```

### Specification Pattern

Encapsulate query logic in reusable objects:

```python
from obc_ingestion_core import Specification

class CompletedTodoSpecification(Specification[Todo]):
    def to_expression(self):
        return Todo.completed == True

class TitleContainsSpecification(Specification[Todo]):
    def __init__(self, text: str):
        self.text = text
    
    def to_expression(self):
        return Todo.title.contains(self.text)

# Usage
completed_todos = await todo_repo.find(CompletedTodoSpecification())
learn_todos = await todo_repo.find(TitleContainsSpecification("Learn"))

# Compose specifications
combined = CompletedTodoSpecification() & TitleContainsSpecification("Learn")
```

### Startup Tasks

Ordered initialization with auto-discovery:

```python
from obc_ingestion_core import StartupTask

class DatabaseInitializationTask(StartupTask):
    order = 30  # Lower numbers run first
    
    async def execute(self) -> None:
        # Initialize database
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        # Configure from YAML
        pass
```

## 📁 Examples

All examples are fully functional and demonstrate real-world usage:

| Example                                                         | Description                               | Status    |
| --------------------------------------------------------------- | ----------------------------------------- | --------- |
| [01_basic_todo.py](examples/01_basic_todo.py)                   | Basic repository pattern with Todo entity | ✅ Working |
| [02_yaml_config.py](examples/02_yaml_config.py)                 | YAML configuration with dotted access     | ✅ Working |
| [03_app_config.py](examples/03_app_config.py)                   | Strongly-typed dataclass configuration    | ✅ Working |
| [04_custom_startup.py](examples/04_custom_startup.py)           | Custom startup tasks with ordering        | ✅ Working |
| [05_database_operations.py](examples/05_database_operations.py) | Advanced database operations              | ✅ Working |
| [06_autodiscovery.py](examples/06_autodiscovery.py)             | Auto-discovery of components              | ✅ Working |
| [07_multi_config.py](examples/07_multi_config.py)               | Multiple configuration sources            | ✅ Working |

### Running Examples

```bash
# Run a specific example
python examples/01_basic_todo.py

# Run all examples
for example in examples/*.py; do
    echo "=== Running $example ==="
    python "$example"
    echo
done
```

## ⚙️ Configuration

### YAML Configuration

```yaml
# config.yaml
database:
  dialect: "sqlite"
  driver: "aiosqlite"
  database: "./db/openbiocure-catalog.db"
  is_memory_db: false

app:
  default_model_provider: "claude"
  agents:
    research_agent:
      model: "claude-3-sonnet"
      temperature: 0.7
      max_tokens: 2000

logging:
  level: INFO
```

### Environment Variables

```python
from obc_ingestion_core import Environment

db_host = Environment.get('HERPAI_DB_HOST', 'localhost')
debug_mode = Environment.get_bool('HERPAI_DEBUG', False)
port = Environment.get_int('HERPAI_PORT', 5432)
```

## 🔧 Extending the Library

### Custom Repositories

```python
from obc_ingestion_core import IRepository, Repository, BaseEntity

class User(BaseEntity):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)

class IUserRepository(IRepository[User], Protocol):
    async def find_by_username(self, username: str) -> Optional[User]: ...

class UserRepository(Repository[User]):
    async def find_by_username(self, username: str) -> Optional[User]:
        return await self.find_one(UserByUsernameSpecification(username))
```

### Custom Startup Tasks

```python
from obc_ingestion_core import StartupTask

class ModelInitializationTask(StartupTask):
    order = 40
    
    async def execute(self) -> None:
        # Initialize AI models
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        self.model_path = config.get('model_path', '/models')
```

### Custom Services

```python
from obc_ingestion_core import engine

class IEmailService(Protocol):
    async def send_email(self, to: str, subject: str, body: str) -> bool: ...

class EmailService:
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        # Implementation
        return True

# Register the service
engine.register(IEmailService, EmailService)
```

## 📚 Documentation

- **[Getting Started Guide](docs/GettingStarted.md)** - Comprehensive guide for new users
- **[Quick Reference](docs/QuickReference.md)** - Fast access to common patterns and code snippets
- **[Bug Tracker](docs/BugTracker.md)** - Known issues and their status
- **[Examples](examples/)** - Working examples demonstrating all features

### Using as a Reference

This project serves as an excellent reference for implementing:
- **Dependency Injection** patterns
- **Repository Pattern** with SQLAlchemy
- **Configuration Management** with YAML and dataclasses
- **Async Database** operations with proper session management
- **Startup Task** orchestration
- **Type-Safe** generic implementations

## 📁 Library Structure

```
obc_ingestion_core/
├── config/           # Configuration management
│   ├── app_config.py
│   ├── environment.py
│   └── yaml_config.py
├── core/             # Core framework
│   ├── engine.py
│   ├── service_collection.py
│   ├── startup_task.py
│   └── type_finder.py
├── data/             # Data access layer
│   ├── db_context.py
│   ├── entity.py
│   ├── repository.py
│   └── specification.py
└── infrastructure/   # Cross-cutting concerns
    ├── caching/
    ├── events/
    └── logging/
```

## 🧪 Requirements

- **Python**: 3.9+
- **SQLAlchemy**: 2.0+
- **PyYAML**: For configuration
- **aiosqlite**: For async SQLite support
- **dataclasses**: Built-in for Python 3.9+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This library is released under the MIT License as part of the OpenBioCure initiative.

## 💬 Community

- **Discord**: [HerpAI Discord Server](https://discord.gg/72dWs7J9)
- **GitHub**: [OpenBioCure/HerpAI-Lib](https://github.com/openbiocure/HerpAI-Lib)

---

## 📋 Changelog

### [3.1.0] - 2025-01-26

#### Added
- Core symbols exposed directly from root package
- `find_one` method to repository pattern
- Enhanced type safety throughout the codebase
- Improved service collection to handle interfaces naturally

#### Fixed
- All examples now working correctly
- Import path issues resolved
- Configuration registration issues fixed
- Database unique constraint handling improved

#### Changed
- Cleaner, more organized documentation
- Simplified import statements
- Better error handling and logging

### [0.2.1] - 2025-04-05

#### Changed
- Renamed library to `obc_ingestion_core`
- Updated project metadata and package name