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

---

# HerpAI-Lib Examples

This directory contains examples demonstrating the key features and patterns of HerpAI-Lib. Each example focuses on a specific aspect of the library to help you understand how to use it effectively in your applications.

## Prerequisites

Before running these examples:

1. Make sure you have HerpAI-Lib installed
2. Ensure you have a `config.yaml` file in your working directory (a sample is provided)

## Running Examples

To run any example:

```bash
python examples/01_basic_todo.py
```

## Example Overview

### 01_basic_todo.py

**Basic Repository Pattern with Entities**

This example demonstrates the core repository pattern with entity creation and dependency injection:

- Defining a `Todo` entity with SQLAlchemy ORM
- Creating a repository interface with custom methods
- Using specifications for querying entities
- Basic CRUD operations (create, read, update)

```python
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

# Create and save a todo
todo = Todo(
    title="Learn HerpAI-Lib",
    description="Implement repository pattern",
    completed=False
)
created_todo = await todo_repository.create(todo)

# Find todos using specifications
completed_todos = await todo_repository.find(CompletedTodoSpecification())
```

Key concepts:
- Entity definition with BaseEntity
- Protocol-based interfaces
- Specification pattern for queries
- Engine resolution of dependencies

### 02_yaml_config.py

**YAML Configuration with Dotted Access**

This example shows how to work with the YAML configuration system:

- Loading configuration from YAML files
- Accessing nested properties with dot notation
- Resolving configuration from the engine

```python
# Get the configuration
config = engine.resolve(YamlConfig)

# Access configuration using dot notation
db_host = config.get('database.host')
db_port = config.get('database.port')
db_name = config.get('database.database')

# Access nested configuration
default_provider = config.get('app.default_model_provider')

# Loop through configuration collections
for agent_name in config.get('app.agents', {}).keys():
    agent_config = config.get(f'app.agents.{agent_name}')
    print(f"Agent: {agent_name}, Model: {agent_config.get('model')}")
```

Key concepts:
- Singleton configuration pattern
- Hierarchical configuration access
- Dynamic configuration retrieval

### 03_app_config.py

**Strongly-Typed AppConfig**

This example demonstrates how to use strongly-typed configuration with dataclasses:

- Accessing typed configuration objects
- Working with nested configuration classes
- Type-safe access to configuration properties
- Database connection through typed configuration

```python
# Get the typed configuration
app_config = AppConfig.get_instance()

# Access strongly typed properties
provider = app_config.default_model_provider  # string
 
# Access nested configuration objects
if app_config.db_config:
    connection_string = app_config.db_config.connection_string
    dialect = app_config.db_config.dialect
    driver = app_config.db_config.driver

# Access collections with type safety
for name, agent in app_config.agents.items():
    model = agent.model  # string
    temperature = agent.temperature  # float
    max_tokens = agent.max_tokens  # int
    cache_enabled = agent.cache  # bool
    
# Get a database session
try:
    session = app_config.get_db_session()
    # Use session for database operations
except Exception as e:
    print(f"Database connection error: {str(e)}")
```

Key concepts:
- Dataclass-based configuration
- Type safety and validation
- Configuration hierarchy

### 04_custom_startup.py

**Custom Startup Tasks**

This example shows how to create and use custom startup tasks:

- Defining startup tasks with execution ordering
- Configuring tasks through YAML
- Task auto-discovery and execution

```python
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
        
        # Database initialization code would go here
        # ...

# In your config.yaml:
# startup_tasks:
#   DatabaseInitializationTask:
#     enabled: true
#     schema: "custom_schema"
#     create_tables: true

# Print information about discovered tasks
for task_name, task in engine._startup_task_executor._tasks.items():
    status = "Enabled" if task.enabled else "Disabled"
    print(f"- {task_name} (Order: {task.order}, Status: {status})")
```

Key concepts:
- Startup task lifecycle
- Task ordering and dependencies
- Configuration-driven task behavior
- Task discovery mechanism

### 05_database_operations.py

**Advanced Database Operations**

This example demonstrates more advanced database operations:

- Defining related entities (User and Post)
- Using foreign keys and relationships
- Complex queries with specifications
- Multi-entity operations

```python
# Define related entities
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

# Define specifications for complex queries
class UserByUsernameSpecification(Specification[User]):
    def __init__(self, username: str):
        self.username = username
    
    def to_expression(self):
        return User.username == self.username

# Usage example
# Create user and posts
user = User(username="johndoe", email="john.doe@example.com")
created_user = await user_repository.create(user)

post = Post(
    title="First Post",
    content="This is my first post!",
    published=False,
    user_id=created_user.id
)
created_post = await post_repository.create(post)

# Find posts by user
user_posts = await post_repository.find(PostByUserIdSpecification(created_user.id))
```

Key concepts:
- Entity relationships
- Advanced specifications
- Repository patterns for related data
- Multi-stage operations

### 06_autodiscovery.py

**Component Auto-Discovery**

This example shows how the engine auto-discovers components:

- Automatic discovery of startup tasks
- Component resolution without manual registration
- Configuration-based component behavior

```python
# Define a new startup task that will be auto-discovered
class ExampleAutoDiscoveredTask(StartupTask):
    """Example task that will be auto-discovered."""
    
    order = 100  # Run late in the sequence
    enabled = True
    
    def execute(self) -> None:
        """Execute the task."""
        logger.info("Auto-discovered task executed!")
        logger.info(f"Task configuration: {self._config}")

# Initialize engine without manually registering anything
engine.initialize()
engine.start()

# The engine will automatically find and execute the task
# Your config.yaml can contain:
# startup_tasks:
#   ExampleAutoDiscoveredTask:
#     enabled: true
#     custom_setting: "value"

# List discovered tasks
print("\nAuto-discovered Startup Tasks:")
for task_name, task in engine._startup_task_executor._tasks.items():
    status = "Enabled" if task.enabled else "Disabled"
    print(f"- {task_name} (Order: {task.order}, Status: {status})")
```

Key concepts:
- Component autodiscovery mechanism
- Dynamic component loading
- Configuration integration

### 07_multi_config.py

**Multiple Configuration Sources**

This example demonstrates working with multiple configuration sources:

- Using both YAML and environment variables
- Environment variable precedence
- Typed environment variable access (string, int, bool)
- Merging configuration from multiple sources

```python
# Define a startup task to load environment variables
class EnvironmentStartupTask(StartupTask):
    """Startup task to load environment variables."""
    
    # Run before configuration
    order = 5
    
    def execute(self) -> None:
        # Set some environment variables
        os.environ["HERPAI_DB_HOST"] = "env-db-host"
        os.environ["HERPAI_DB_PORT"] = "5433"
        os.environ["HERPAI_API_KEY"] = "env-api-key-123"
        os.environ["HERPAI_DEBUG"] = "true"

# Access YAML configuration
yaml_config = engine.resolve(YamlConfig)
yaml_db_host = yaml_config.get('database.host')

# Access environment variables with type conversion
env_db_host = Environment.get('HERPAI_DB_HOST')  # string
env_db_port = Environment.get_int('HERPAI_DB_PORT')  # integer
api_key = Environment.get('HERPAI_API_KEY')  # string
debug_mode = Environment.get_bool('HERPAI_DEBUG')  # boolean

# Merge configuration (environment takes precedence)
db_host = Environment.get('HERPAI_DB_HOST') or yaml_config.get('database.host')
db_port = Environment.get_int('HERPAI_DB_PORT') or yaml_config.get('database.port')
```

Key concepts:
- Configuration sources and precedence
- Environment variable integration
- Type conversion for config values

## Configuration Examples

For these examples to work properly, you'll need a `config.yaml` file with content similar to:

```yaml
app:
  default_model_provider: "example-provider"
  agents:
    test-agent:
      model_provider: "example-provider"
      model: "example-model"
      prompt_version: "v1"
      cache: true
      max_tokens: 1000
      temperature: 0.5
      tags: ["example", "test"]

database:
  host: "localhost"
  port: 5432
  database: "test_db"
  username: "test_user"
  password: "test_password"
  dialect: "sqlite"
  driver: "aiosqlite"

startup_tasks:
  ConfigurationStartupTask:
    enabled: true
  DatabaseInitializationTask:
    enabled: true
    schema: "example"
    create_tables: true
  ModelInitializationTask:
    enabled: true
    default_model: "example-model"
    preload: false
  ExampleAutoDiscoveredTask:
    enabled: true
    example_setting: "example value"
```

## Best Practices

When using HerpAI-Lib based on these examples:

1. **Follow Interface Segregation**: Define focused interfaces like `ITodoRepository` with specific methods
2. **Use Specifications**: Encapsulate query logic in specifications like `CompletedTodoSpecification`
3. **Layer Configuration**: Use YAML for general settings and environment variables for secrets/deployment-specific values
4. **Order Startup Tasks**: Assign appropriate order values to ensure proper initialization sequence
5. **Leverage Auto-Discovery**: Let the engine discover components instead of manual registration

---

# HerpAI-Lib Example File Documentation

## 01_basic_todo.py

This example demonstrates the fundamental repository pattern with entity creation and dependency injection.

**Key Components:**

- `Todo` Entity: Represents a task with title, description, and completion status
- `ITodoRepository`: Interface defining custom methods for todo operations
- `CompletedTodoSpecification`: Filter criteria for completed todos
- `TitleContainsSpecification`: Filter criteria for todos containing specific text

```python
# Define a Todo entity
class Todo(BaseEntity):
    """Todo entity for task management."""
    __tablename__ = "todos"
    
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)

# Define specifications
class CompletedTodoSpecification(Specification[Todo]):
    def to_expression(self):
        return Todo.completed == True

class TitleContainsSpecification(Specification[Todo]):
    def __init__(self, text: str):
        self.text = text
    
    def to_expression(self):
        return Todo.title.contains(self.text)

# Async main function
async def main():
    # Initialize and start the engine 
    engine.initialize()
    engine.start()
    
    # Resolve the todo repository
    todo_repository = engine.resolve(ITodoRepository)
    
    # Create and save a Todo
    todo = Todo(
        id=str(uuid.uuid4()),
        title="Learn HerpAI-Lib",
        description="Implement repository pattern with dependency injection",
        completed=False
    )
    
    created_todo = await todo_repository.create(todo)
    
    # Find todos by specification
    completed_todos = await todo_repository.find(CompletedTodoSpecification())
```

**What This Example Shows:**

1. How to define entities using SQLAlchemy ORM and BaseEntity
2. Creating protocol-based repository interfaces
3. Implementing specifications for flexible queries
4. Using the engine for dependency resolution
5. Performing basic CRUD operations (create, update, find)

## 02_yaml_config.py

This example demonstrates how to use the YAML configuration system with dotted access notation.

**Key Components:**

- `YamlConfig`: Singleton configuration provider
- Dotted access: `config.get('database.host')` syntax
- Nested iteration: Access to nested configuration structures

```python
async def main():
    # Initialize and start the engine with auto-discovered tasks
    engine.initialize()
    engine.start()
    
    # Get the configuration
    config = engine.resolve(YamlConfig)
    
    # Access configuration using dot notation
    print("\nDatabase Configuration:")
    print(f"Host: {config.get('database.host')}")
    print(f"Port: {config.get('database.port')}")
    print(f"Database: {config.get('database.database')}")
    
    print("\nDefault Model Provider:")
    print(f"{config.get('app.default_model_provider')}")
    
    # Access nested configuration structures
    print("\nAgent Configurations:")
    for agent_name in config.get('app.agents', {}).keys():
        print(f"\n{agent_name}:")
        agent_config = config.get(f'app.agents.{agent_name}')
        print(f"  Model: {agent_config.get('model')}")
        print(f"  Temperature: {agent_config.get('temperature')}")
        print(f"  Tags: {', '.join(agent_config.get('tags', []))}")
```

**What This Example Shows:**

1. How to resolve configuration from the engine
2. Accessing nested properties with dot notation
3. Working with configuration sections and groups
4. Iterating through configuration collections

## 03_app_config.py

This example demonstrates how to use strongly-typed configuration with dataclasses.

**Key Components:**

- `AppConfig`: Strongly-typed configuration object
- Nested configuration classes: Database and agent configurations
- Type-safe property access

**What This Example Shows:**

1. Accessing typed configuration singleton
2. Working with nested configuration classes
3. Type-safe access to configuration properties
4. Database connection through typed configuration
5. Handling optional configuration sections

## 04_custom_startup.py

This example demonstrates how to create and use custom startup tasks with ordering and configuration.

**Key Components:**

- `DatabaseInitializationTask`: Custom task for database setup
- `ModelInitializationTask`: Custom task for AI model initialization
- Task ordering: Execution sequence control
- Task configuration: Task-specific settings

**What This Example Shows:**

1. Defining startup tasks with specific execution order
2. Accessing task-specific configuration
3. Task logging and initialization process
4. Viewing and debugging task configuration

## 05_database_operations.py

This example demonstrates more complex database operations using the repository pattern.

**Key Components:**

- `User` and `Post` entities with relationship
- Repository interfaces with domain-specific methods
- Entity-specific specifications
- Multi-entity operations

```python
# Define entities with relationships
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

# Define repository interfaces with domain-specific methods
class IUserRepository(IRepository[User], Protocol):
    async def find_by_username(self, username: str) -> Optional[User]: ...
    async def find_by_email(self, email: str) -> Optional[User]: ...

class IPostRepository(IRepository[Post], Protocol):
    async def find_by_user_id(self, user_id: str) -> List[Post]: ...
    async def find_published(self) -> List[Post]: ...
    async def publish(self, post: Post) -> Post: ...

# Multi-entity operation example
# Create user
user = User(username="johndoe", email="john.doe@example.com")
created_user = await user_repository.create(user)

# Create posts for user
post1 = Post(title="First Post", content="Content", user_id=created_user.id)
created_post1 = await post_repository.create(post1)

# Find posts for user using specification
user_posts = await post_repository.find(PostByUserIdSpecification(created_user.id))
```

**What This Example Shows:**

1. Defining related entities with foreign keys
2. Creating repository interfaces for different entity types
3. Implementing specifications for complex queries
4. Working with multiple repositories in a single operation

## 06_autodiscovery.py

This example demonstrates how the engine auto-discovers startup tasks and other components.

**Key Components:**

- `ExampleAutoDiscoveredTask`: Custom task that is auto-discovered
- Task discovery mechanism
- Configuration integration

**What This Example Shows:**

1. How tasks are automatically discovered
2. Task configuration and execution
3. Listing discovered tasks and their status
4. Working with discovered configuration

## 07_multi_config.py

This example demonstrates how to work with multiple configuration sources.

**Key Components:**

- `YamlConfig`: File-based configuration
- `Environment`: Environment variable configuration
- `EnvironmentStartupTask`: Sets up environment variables
- Configuration precedence

```python
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
    
    # Access different configuration sources
    print("\nYAML Configuration:")
    print(f"Database Host (YAML): {yaml_config.get('database.host')}")
    
    print("\nEnvironment Variables:")
    print(f"Database Host (ENV): {Environment.get('HERPAI_DB_HOST')}")
    print(f"Database Port (ENV): {Environment.get_int('HERPAI_DB_PORT')}")
    print(f"API Key (ENV): {Environment.get('HERPAI_API_KEY')}")
    print(f"Debug Mode (ENV): {Environment.get_bool('HERPAI_DEBUG')}")
    
    # Merging configuration with precedence
    db_host = Environment.get('HERPAI_DB_HOST') or yaml_config.get('database.host')
    db_port = Environment.get_int('HERPAI_DB_PORT') or yaml_config.get('database.port')
```

**What This Example Shows:**

1. Working with both YAML and environment variables
2. Environment variable precedence
3. Typed environment variable access
4. Merging configuration from multiple sources