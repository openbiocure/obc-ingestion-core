# Quick Reference Guide

This guide provides quick access to the most commonly used components and patterns from the OBC Ingestion Core library.

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/openbiocure/obc-ingestion-core.git
cd obc-ingestion-core
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"

# Run examples
make run-examples

# Run tests
make test
```

## 📁 Essential Files to Copy

### Core DI Engine
```bash
# Copy these for dependency injection:
cp obc_ingestion_core/core/engine.py your_project/
cp obc_ingestion_core/core/service_collection.py your_project/
cp obc_ingestion_core/core/service_scope.py your_project/
cp obc_ingestion_core/core/singleton.py your_project/
```

### Repository Pattern
```bash
# Copy these for repository pattern:
cp obc_ingestion_core/data/repository.py your_project/
cp obc_ingestion_core/data/specification.py your_project/
cp obc_ingestion_core/data/entity.py your_project/
```

### Configuration Management
```bash
# Copy these for configuration:
cp obc_ingestion_core/config/app_config.py your_project/
cp obc_ingestion_core/config/yaml_config.py your_project/
cp obc_ingestion_core/config/environment.py your_project/
```

### Database Management
```bash
# Copy these for database handling:
cp obc_ingestion_core/data/db_context.py your_project/
cp obc_ingestion_core/data/db_context_startup_task.py your_project/
```

## 🔧 Common Code Snippets

### Basic Engine Setup
```python
from obc_ingestion_core.core.engine import Engine

async def main():
    await Engine.start()
    # Your code here
    await Engine.stop()

# Run
import asyncio
asyncio.run(main())
```

### Entity Definition
```python
from obc_ingestion_core.data.entity import BaseEntity
from sqlalchemy import Column, String, Integer

class User(BaseEntity):
    __tablename__ = "users"
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    age = Column(Integer)
```

### Repository Implementation
```python
from obc_ingestion_core.data.repository import Repository

class UserRepository(Repository[User]):
    def __init__(self, session, entity_type):
        super().__init__(session, entity_type)
    
    async def find_by_email(self, email: str):
        return await self.find_one(UserByEmailSpecification(email))
```

### Specification Pattern
```python
from obc_ingestion_core.data.specification import Specification

class UserByEmailSpecification(Specification[User]):
    def __init__(self, email: str):
        self.email = email
    
    def to_expression(self):
        return User.email == self.email
```

### Configuration Setup
```python
from obc_ingestion_core.config.app_config import AppConfig

config = AppConfig(
    database_url="sqlite+aiosqlite:///app.db",
    agent_name="my-app"
)
```

### Service Registration
```python
engine = Engine.current()
engine.register(IUserService, UserService)
engine.register(UserRepository, UserRepository)
```

### Service Resolution
```python
engine = Engine.current()
user_service = engine.resolve(IUserService)
user_repo = engine.resolve(UserRepository)
```

## 🗂️ Project Structure Template

```
your_project/
├── src/
│   ├── core/              # DI engine, service collection
│   ├── data/              # Repositories, entities, specifications
│   ├── config/            # Configuration management
│   ├── domain/            # Domain models
│   └── utils/             # Utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── mocks/
├── examples/
├── config/
│   └── config.yaml
├── pyproject.toml
└── README.md
```

## 📋 Dependencies

### Required Dependencies
```toml
[project]
dependencies = [
    "sqlalchemy>=2.0.0",
    "pyyaml>=6.0",
    "aiosqlite>=0.17.0",
    "greenlet>=2.0.0"
]
```

### Development Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.18.0",
    "pytest-cov>=4.0.0",
    "black",
    "isort",
    "mypy",
    "flake8>=7.0.0"
]
```

## 🔍 Key Patterns

### 1. Dependency Injection
- **Engine**: Central DI container
- **ServiceCollection**: Service registration and resolution
- **ServiceScope**: Lifetime management (singleton, scoped, transient)

### 2. Repository Pattern
- **IRepository<T>**: Generic interface
- **Repository<T>**: Base implementation
- **Specification**: Query encapsulation

### 3. Configuration
- **AppConfig**: Strongly-typed configuration
- **YamlConfig**: File-based configuration
- **Environment**: Environment variable integration

### 4. Database
- **DbContext**: Async database context
- **Session Management**: Context manager pattern
- **Connection Pooling**: Optimized connection handling

## 🧪 Testing Patterns

### Unit Test Template
```python
import pytest
from obc_ingestion_core.core.engine import Engine

@pytest.mark.asyncio
async def test_my_component():
    await Engine.start()
    try:
        component = Engine.current().resolve(MyComponent)
        result = await component.do_something()
        assert result is not None
    finally:
        await Engine.stop()
```

### Integration Test Template
```python
@pytest.mark.asyncio
async def test_database_operation():
    db_context = DbContext("sqlite+aiosqlite:///:memory:")
    await db_context.initialize()
    
    async with db_context.session_context() as session:
        # Your test code here
        pass
    
    await db_context.close()
```

## 🚨 Common Issues & Solutions

### Import Errors
```bash
# Solution: Install in development mode
pip install -e .
```

### Database Connection Issues
```python
# Check your database URL
config = AppConfig(database_url="sqlite+aiosqlite:///app.db")
```

### Service Not Found
```python
# Register before resolving
engine.register(IMyService, MyServiceImpl)
service = engine.resolve(IMyService)
```

### Async/Await Issues
```python
# Use async functions and await
async def main():
    await Engine.start()
    # ... your code ...
    await Engine.stop()

asyncio.run(main())
```

## 📚 Learning Path

1. **Start with Examples**: Run `make run-examples`
2. **Study Core Components**: Focus on `engine.py` and `repository.py`
3. **Understand Patterns**: DI, Repository, Specification
4. **Practice**: Create your own entities and repositories
5. **Test**: Write tests for your components
6. **Extend**: Add custom functionality

## 🔗 Useful Links

- [Full Documentation](docs/GettingStarted.md)
- [Bug Tracker](docs/BugTracker.md)
- [Examples Directory](examples/)
- [Test Suite](tests/)
- [GitHub Repository](https://github.com/openbiocure/obc-ingestion-core)

## 💡 Pro Tips

1. **Use Type Hints**: All components are fully typed
2. **Follow Patterns**: Stick to established patterns for consistency
3. **Write Tests**: Every component should have tests
4. **Use Context Managers**: For database sessions and resources
5. **Configure Logging**: Enable debug logging for troubleshooting
6. **Version Control**: Use semantic versioning for your components 