# Getting Started with OBC Ingestion Core

This guide will help you get started with the OBC Ingestion Core library, whether you're using it as a dependency in your project or using it as a reference for building similar functionality.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Using as a Reference](#using-as-a-reference)
5. [Architecture Overview](#architecture-overview)
6. [Key Concepts](#key-concepts)
7. [Examples](#examples)
8. [Configuration](#configuration)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

### Clone the Repository

```bash
git clone https://github.com/openbiocure/obc-ingestion-core.git
cd obc-ingestion-core
```

### Install Dependencies

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Run Examples

```bash
# Run all examples
make run-examples

# Or run individual examples
python examples/01_basic_todo.py
python examples/02_yaml_config.py
python examples/03_app_config.py
```

## Installation

### As a Dependency

If you want to use this library in your project:

```bash
pip install obc-ingestion-core
```

### From Source

```bash
git clone https://github.com/openbiocure/obc-ingestion-core.git
cd obc-ingestion-core
pip install -e .
```

## Basic Usage

### 1. Initialize the Engine

```python
from obc_ingestion_core.core.engine import Engine

# Start the engine (this will auto-discover and register components)
await Engine.start()
```

### 2. Configure Your Application

```python
from obc_ingestion_core.config.app_config import AppConfig

# Create configuration
config = AppConfig(
    database_url="sqlite+aiosqlite:///myapp.db",
    agent_name="my-application"
)
```

### 3. Define Your Entities

```python
from obc_ingestion_core.data.entity import BaseEntity
from sqlalchemy import Column, String, Integer

class User(BaseEntity):
    __tablename__ = "users"
    
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer)
```

### 4. Create Repositories

```python
from obc_ingestion_core.data.repository import Repository

class UserRepository(Repository[User]):
    def __init__(self, session, entity_type):
        super().__init__(session, entity_type)
```

### 5. Use the Repository Pattern

```python
# Get a repository instance
user_repo = Engine.current().resolve(UserRepository)

# Create a user
user = await user_repo.create(
    username="john_doe",
    email="john@example.com",
    age=30
)

# Find users
users = await user_repo.find(UserActiveSpecification())
```

## Using as a Reference

### Project Structure Reference

This project demonstrates several architectural patterns and best practices:

```
obc-ingestion-core/
├── obc_ingestion_core/           # Main package
│   ├── config/                   # Configuration management
│   ├── core/                     # Core DI and engine
│   ├── data/                     # Data access layer
│   ├── domain/                   # Domain models
│   └── utils/                    # Utilities
├── examples/                     # Usage examples
├── tests/                        # Test suite
├── docs/                         # Documentation
└── pyproject.toml               # Project configuration
```

### Key Patterns to Study

1. **Dependency Injection Pattern**
   - `Engine` class as the DI container
   - `ServiceCollection` for service registration
   - Service lifetime management (singleton, scoped, transient)

2. **Repository Pattern**
   - Generic `IRepository<T>` interface
   - `Repository<T>` base implementation
   - Specification pattern for queries

3. **Configuration Management**
   - Dataclass-based configuration (`AppConfig`)
   - YAML configuration support (`YamlConfig`)
   - Environment variable integration

4. **Startup Task Pattern**
   - Ordered initialization
   - Auto-discovery of startup tasks
   - Cleanup handling

### Copying Specific Components

#### 1. Dependency Injection Engine

```python
# Copy these files for DI functionality:
# - obc_ingestion_core/core/engine.py
# - obc_ingestion_core/core/service_collection.py
# - obc_ingestion_core/core/service_scope.py
# - obc_ingestion_core/core/singleton.py
```

#### 2. Repository Pattern

```python
# Copy these files for repository pattern:
# - obc_ingestion_core/data/repository.py
# - obc_ingestion_core/data/specification.py
# - obc_ingestion_core/data/entity.py
```

#### 3. Configuration Management

```python
# Copy these files for configuration:
# - obc_ingestion_core/config/app_config.py
# - obc_ingestion_core/config/yaml_config.py
# - obc_ingestion_core/config/environment.py
```

#### 4. Database Context

```python
# Copy these files for database management:
# - obc_ingestion_core/data/db_context.py
# - obc_ingestion_core/data/db_context_startup_task.py
```

## Architecture Overview

### Core Components

1. **Engine**: Central dependency injection container
2. **ServiceCollection**: Manages service registrations and lifetimes
3. **DbContext**: Handles database connections and sessions
4. **Repository**: Generic data access layer
5. **Configuration**: Application settings management

### Data Flow

```
Application Startup
    ↓
Engine.start()
    ↓
Auto-discover components
    ↓
Register services
    ↓
Execute startup tasks
    ↓
Application ready
```

### Service Resolution

```
Client requests service
    ↓
Engine.resolve(ServiceType)
    ↓
ServiceCollection.get_service()
    ↓
Create instance (if needed)
    ↓
Return service instance
```

## Key Concepts

### 1. Dependency Injection

The engine provides a simple but powerful DI container:

```python
# Register services
engine.register(IMyService, MyServiceImpl)

# Resolve services
service = engine.resolve(IMyService)
```

### 2. Repository Pattern

Repositories abstract data access:

```python
class UserRepository(Repository[User]):
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one(UserByEmailSpecification(email))
```

### 3. Specification Pattern

Specifications encapsulate query logic:

```python
class UserByEmailSpecification(Specification[User]):
    def __init__(self, email: str):
        self.email = email
    
    def to_expression(self) -> BinaryExpression:
        return User.email == self.email
```

### 4. Configuration Management

Multiple configuration sources:

```python
# AppConfig for strongly-typed settings
config = AppConfig(database_url="sqlite:///app.db")

# YamlConfig for file-based configuration
yaml_config = YamlConfig("config.yaml")
```

## Examples

### Basic Todo Application

See `examples/01_basic_todo.py` for a complete example of:
- Entity definition
- Repository implementation
- Basic CRUD operations

### Configuration Examples

See `examples/02_yaml_config.py` and `examples/03_app_config.py` for:
- YAML configuration loading
- Strongly-typed configuration
- Environment variable integration

### Database Operations

See `examples/05_database_operations.py` for:
- Advanced database operations
- Transaction handling
- Complex queries

### Auto-discovery

See `examples/06_autodiscovery.py` for:
- Component auto-discovery
- Startup task registration
- Plugin architecture

## Configuration

### Environment Variables

```bash
export DATABASE_URL="sqlite+aiosqlite:///app.db"
export AGENT_NAME="my-application"
export LOG_LEVEL="INFO"
```

### YAML Configuration

```yaml
# config.yaml
database:
  url: "sqlite+aiosqlite:///app.db"
  echo: false

agent:
  name: "my-application"
  version: "1.0.0"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### AppConfig Usage

```python
from obc_ingestion_core.config.app_config import AppConfig

config = AppConfig(
    database_url="sqlite+aiosqlite:///app.db",
    agent_name="my-application",
    log_level="INFO"
)
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_engine.py

# Run with coverage
pytest tests --cov=obc_ingestion_core --cov-report=html
```

### Test Structure

```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── mocks/                   # Mock implementations
└── conftest.py             # Test configuration
```

### Writing Tests

```python
import pytest
from obc_ingestion_core.core.engine import Engine

@pytest.mark.asyncio
async def test_my_component():
    # Setup
    await Engine.start()
    
    # Test
    component = Engine.current().resolve(MyComponent)
    result = await component.do_something()
    
    # Assert
    assert result is not None
    
    # Cleanup
    await Engine.stop()
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'obc_ingestion_core'`

**Solution**: Install the package in development mode:
```bash
pip install -e .
```

#### 2. Database Connection Issues

**Problem**: SQLAlchemy connection errors

**Solution**: Check your database URL and ensure the database exists:
```python
# For SQLite
config = AppConfig(database_url="sqlite+aiosqlite:///app.db")

# For PostgreSQL
config = AppConfig(database_url="postgresql+asyncpg://user:pass@localhost/db")
```

#### 3. Service Resolution Errors

**Problem**: `Service not found` errors

**Solution**: Ensure services are registered before resolving:
```python
# Register the service
engine.register(IMyService, MyServiceImpl)

# Then resolve
service = engine.resolve(IMyService)
```

#### 4. Async/Await Issues

**Problem**: Runtime errors about async/await

**Solution**: Ensure you're using async functions and awaiting async operations:
```python
async def main():
    await Engine.start()
    # ... your code ...
    await Engine.stop()

# Run with asyncio
import asyncio
asyncio.run(main())
```

### Debug Mode

Enable debug logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check the [examples](examples/) directory for working code
2. Review the [test files](tests/) for usage patterns
3. Check the [BugTracker](docs/BugTracker.md) for known issues
4. Open an issue on GitHub for bugs or feature requests

## Next Steps

1. **Explore Examples**: Run through all examples to understand the patterns
2. **Study Architecture**: Review the core components and their interactions
3. **Customize**: Adapt the patterns to your specific use case
4. **Extend**: Add your own components following the established patterns
5. **Test**: Write comprehensive tests for your custom components

## Contributing

If you find this project useful and want to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 