# OpenBioCure CoreLib Source Code Index

## Project Overview

**OpenBioCure_CoreLib** is a foundational Python library for the HerpAI platform that provides:
- Dependency Injection (DI) engine with service management
- Repository pattern implementation with SQLAlchemy
- Specification pattern for query filtering
- Configuration management (YAML + dataclasses)
- Auto-discovery startup system
- Async/await support throughout

**Version**: 3.1.0  
**Python**: 3.9+  
**License**: MIT

## Architecture Overview

```
openbiocure_corelib/
├── core/           # Dependency injection and application lifecycle
├── data/           # Repository pattern and database abstractions
├── config/         # Configuration management
├── infrastructure/ # Cross-cutting concerns (caching, events, logging)
└── utils/          # Utility functions
```

## Core Components

### 1. Engine (`core/engine.py`)

**Purpose**: Central DI container and application lifecycle manager

**Key Features**:
- Singleton pattern implementation
- Service registration and resolution
- Auto-discovery of repositories and startup tasks
- Application startup/shutdown coordination

**Key Methods**:
```python
# Initialize the engine
engine = Engine.initialize()

# Start the application (runs startup tasks)
await engine.start()

# Resolve services
service = engine.resolve(IServiceType)

# Register services
engine.register(IServiceType, ServiceImplementation)

# Stop the application
await engine.stop()
```

**Lifecycle**:
1. `initialize()` - Sets up engine and registers core services
2. `start()` - Executes startup tasks in order
3. `stop()` - Cleans up resources

### 2. Repository Pattern (`data/repository.py`)

**Purpose**: Abstract data access layer with CRUD operations

**Key Interfaces**:
```python
class IRepository(Generic[T], Protocol):
    async def create(self, entity=None, **kwargs) -> T
    async def get(self, id: str) -> Optional[T]
    async def update(self, id_or_entity: Union[str, T], **kwargs) -> Optional[T]
    async def delete(self, id: str) -> bool
    async def find(self, spec: ISpecification[T]) -> List[T]
```

**Implementation**: `Repository[T]` provides SQLAlchemy-based implementation

**Usage Example**:
```python
# Define entity
class Todo(BaseEntity):
    title: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)

# Define repository interface
class ITodoRepository(IRepository[Todo], Protocol):
    pass

# Auto-registered by engine
todo_repo = engine.resolve(ITodoRepository)
todo = await todo_repo.create(title="Learn CoreLib", completed=False)
```

### 3. Specification Pattern (`data/specification.py`)

**Purpose**: Encapsulate query logic in reusable objects

**Key Interfaces**:
```python
class ISpecification(Generic[T], Protocol):
    def is_satisfied_by(self, entity: T) -> bool
    def to_expression(self) -> Any  # SQLAlchemy expression

class Specification(Generic[T], ISpecification[T]):
    def and_(self, other: ISpecification[T]) -> ISpecification[T]
    def or_(self, other: ISpecification[T]) -> ISpecification[T]
```

**Usage Example**:
```python
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
```

### 4. Configuration Management

#### YAML Configuration (`config/yaml_config.py`)
```python
class YamlConfig:
    def load(self, config_file: str) -> None
    def get(self, key: str, default: Any = None) -> Any  # Supports dot notation
    def get_connection_string(self) -> str
```

#### Dataclass Configuration (`config/app_config.py`)
```python
@dataclass
class DatabaseConfig:
    dialect: str = "sqlite"
    driver: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = "herpai.db"
    username: Optional[str] = None
    password: Optional[str] = None
    is_memory_db: bool = False

@dataclass
class AppConfig:
    default_model_provider: str = "claude"
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    db_config: Optional[DatabaseConfig] = None
```

### 5. Startup Tasks (`core/startup_task.py`)

**Purpose**: Ordered initialization steps during application startup

**Key Features**:
- Auto-discovery of startup tasks
- Configurable execution order
- Async execution support
- Configuration injection

**Usage Example**:
```python
class DatabaseInitializationTask(StartupTask):
    order = 30  # Lower numbers run first
    
    async def execute(self) -> None:
        # Initialize database
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        # Configure from YAML
        pass
```

### 6. Database Context (`data/db_context.py`)

**Purpose**: Manage SQLAlchemy async engine and sessions

**Key Features**:
- Async SQLAlchemy support
- Connection string or config-based initialization
- Schema creation
- Session management

**Usage**:
```python
# Auto-registered by engine
db_context = engine.resolve(IDbContext)
session = db_context.session

# Execute raw SQL
result = await db_context.execute(text("SELECT * FROM todos"))
```

### 7. Type Discovery (`core/type_finder.py`)

**Purpose**: Auto-discover classes implementing specific interfaces

**Key Features**:
- Module scanning for implementations
- Generic type resolution
- Protocol/interface detection
- Caching for performance

**Usage**:
```python
type_finder = TypeFinder()
startup_tasks = type_finder.find_classes_of_type(StartupTask)
repositories = type_finder.find_generic_implementations(IRepository)
```

## Service Collection (`core/service_collection.py`)

**Purpose**: Internal registry for service definitions and lifetimes

**Lifetime Types**:
- **Singleton**: One instance for the entire application
- **Scoped**: One instance per scope
- **Transient**: New instance each time

## Entity Base (`data/entity.py`)

**Purpose**: Base class for all domain entities

**Features**:
```python
class BaseEntity(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC)
    )
    tenant_id: Mapped[Optional[str]] = mapped_column(default=None)
```

## Configuration Examples

### Basic YAML Configuration
```yaml
database:
  dialect: "sqlite"
  driver: "aiosqlite"
  database: "./db/herpai.db"
  is_memory_db: false

app:
  default_model_provider: "claude"
  agents:
    research_agent:
      model: "claude-3-sonnet"
      temperature: 0.7
      max_tokens: 2000
```

### Environment Variables (`config/environment.py`)
```python
class Environment:
    @staticmethod
    def get(key: str, default: str = "") -> str
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool
    @staticmethod
    def get_int(key: str, default: int = 0) -> int
```

## Testing Infrastructure

### Test Configuration (`tests/conftest.py`)
- In-memory SQLite databases for testing
- CI environment detection
- Engine initialization fixtures
- Mock implementations

### Test Patterns
```python
@pytest.fixture(scope="function")
async def initialized_engine(test_config_file):
    Engine._instance = None
    test_engine = Engine.initialize()
    await test_engine.start()
    yield test_engine
    await test_engine.stop()
```

## Development Workflow

### Makefile Commands
```bash
# Development setup
make venv          # Create virtual environment
make dev-install   # Install with dev dependencies
make init          # Setup pre-commit hooks

# Quality checks
make lint          # Run linters (flake8, mypy, black, isort)
make test          # Run tests with coverage
make check         # Run all quality checks

# Building and publishing
make build         # Build package distributions
make publish-pypi  # Publish to PyPI
```

### Project Structure
```
obc-ingestion-core/
├── openbiocure_corelib/    # Main library code
├── examples/               # Usage examples
├── tests/                  # Test suite
├── config.yaml            # Default configuration
├── pyproject.toml         # Project metadata
├── Makefile              # Development commands
└── README.md             # Documentation
```

## Key Design Patterns

### 1. Dependency Injection
- Service registration and resolution
- Lifetime management (singleton, scoped, transient)
- Interface-based programming

### 2. Repository Pattern
- Abstract data access
- Entity-specific repositories
- Specification-based queries

### 3. Specification Pattern
- Encapsulated query logic
- Composable specifications
- SQLAlchemy expression generation

### 4. Auto-Discovery
- Type scanning and registration
- Startup task discovery
- Repository auto-registration

### 5. Configuration Management
- Multiple configuration sources
- Type-safe dataclass configuration
- Environment variable support

## Usage Examples

### Basic Application Setup
```python
import asyncio
from openbiocure_corelib import engine

async def main():
    # Initialize and start the engine
    engine.initialize()
    await engine.start()
    
    # Use the application
    todo_repo = engine.resolve(ITodoRepository)
    todos = await todo_repo.find(CompletedTodoSpecification())
    
    # Clean up
    await engine.stop()

asyncio.run(main())
```

### Custom Repository Implementation
```python
class TodoRepository(Repository[Todo]):
    async def find_completed(self) -> List[Todo]:
        return await self.find(CompletedTodoSpecification())
    
    async def find_by_title(self, title: str) -> List[Todo]:
        return await self.find(TitleContainsSpecification(title))
```

### Custom Startup Task
```python
class DatabaseSchemaTask(StartupTask):
    order = 20
    
    async def execute(self) -> None:
        db_context = engine.resolve(IDbContext)
        await db_context.create_schema()
```

## Dependencies

### Core Dependencies
- `sqlalchemy>=2.0.0` - Database ORM
- `pyyaml>=6.0` - YAML configuration
- `aiosqlite>=0.17.0` - Async SQLite support
- `greenlet>=2.0.0` - Async support

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.18.0` - Async test support
- `black` - Code formatting
- `mypy` - Type checking
- `flake8>=7.0.0` - Linting

## Performance Considerations

### Type Discovery
- Caches loaded modules for faster scanning
- Filters modules to avoid unnecessary processing
- Supports incremental module loading

### Database Operations
- Uses SQLAlchemy async for non-blocking operations
- Connection pooling for efficient resource usage
- Transaction management for data consistency

### Service Resolution
- Singleton services cached for lifetime
- Lazy initialization of services
- Scope-based service management

## Security Features

### Configuration Security
- Environment variable support for sensitive data
- Validation of configuration values
- Secure connection string generation

### Database Security
- Parameterized queries to prevent SQL injection
- Connection string validation
- Transaction isolation

## Error Handling

### Graceful Degradation
- Default configurations when files missing
- Fallback to in-memory databases
- Warning logs for non-critical failures

### Exception Types
- `ConfigError` - Configuration-related errors
- `RuntimeError` - Engine lifecycle errors
- `ValueError` - Service resolution errors

## Future Considerations

### Potential Enhancements
- Event system for cross-cutting concerns
- Caching infrastructure
- Metrics and monitoring
- Plugin system for extensions

### Scalability
- Distributed service discovery
- Multi-tenant support
- Horizontal scaling considerations
- Performance monitoring

This index provides a comprehensive overview of the OpenBioCure CoreLib source code, its architecture, and usage patterns. The library is designed to be extensible, testable, and maintainable while providing a solid foundation for building applications with modern Python patterns. 