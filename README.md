# HerpAI-Lib

[![Makefile CI](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml)

**HerpAI-Lib** is the foundational core library for the [HerpAI](https://github.com/openbiocure/HerpAI) platform. It provides shared infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern used across HerpAI agents and services.

## 📋 Documentation

- [CHANGELOG](CHANGELOG.md) - See what's new and what's changed

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
# Install from GitHub
pip install git+https://github.com/openbiocure/HerpAI-Lib.git

# For development
git clone https://github.com/openbiocure/HerpAI-Lib.git
cd HerpAI-Lib
pip install -e .
```

## 🧪 Development

### Building

```bash
# Create a virtual environment
make venv

# Install development dependencies
make dev-install

# Format code
make format

# Lint code
make lint
```

### Testing

```bash
# Run all tests
make test

# Run a specific test file
pytest tests/unit/test_engine.py

# Run tests with coverage
pytest tests/ --cov=openbiocure_corelib --cov-report=term-missing
```

### Building Packages

```bash
# Build package
make build

# Clean build artifacts
make clean
```

## 📋 Examples

| Example | Description |
|---------|-------------|
| [01_basic_todo.py](examples/01_basic_todo.py) | Demonstrates basic repository pattern with a Todo entity, including CRUD operations and dependency injection |
| [02_yaml_config.py](examples/02_yaml_config.py) | Shows how to work with YAML configuration files, including environment variables and dotted notation access |
| [03_app_config.py](examples/03_app_config.py) | Illustrates strongly-typed configuration using dataclasses with validation and inheritance |
| [04_custom_startup.py](examples/04_custom_startup.py) | Shows how to create and order custom startup tasks with dependencies and async support |
| [05_database_operations.py](examples/05_database_operations.py) | Comprehensive example of database operations using repositories, specifications, and async patterns |
| [06_autodiscovery.py](examples/06_autodiscovery.py) | Demonstrates automatic discovery and registration of components, repositories, and startup tasks |
| [07_multi_config.py](examples/07_multi_config.py) | Shows how to work with multiple configuration sources and hierarchical configuration |

### Example Domains
The `examples/domain/` directory contains sample domain models and business logic implementations.

### Repository Examples
The `examples/repository/` directory shows advanced repository pattern implementations with:
- Custom specifications
- Complex queries
- Relationship handling
- Bulk operations

### Configuration Examples
The `examples/config/` directory demonstrates various configuration scenarios including:
- Environment-specific configs
- Validation rules
- Hot reload
- Secret management

## 📁 Library Structure

```
openbiocure_corelib/
├── core/                     # Core engine components
│   ├── engine.py            # Main DI container and application lifecycle
│   ├── interfaces.py        # Core interfaces
│   ├── service_collection.py # Service registration and resolution
│   ├── service_scope.py     # Scoped service management
│   ├── startup_task.py      # Base startup task definition
│   ├── startup_task_executor.py # Startup orchestration
│   ├── type_finder.py       # Dynamic type discovery
│   └── singleton.py         # Singleton pattern implementation
│
├── config/                   # Configuration management
│   ├── settings.py          # Settings management
│   ├── environment.py       # Environment variables
│   ├── yaml_config.py       # YAML configuration
│   └── app_config.py        # Application configuration
│
├── data/                     # Data access layer
│   ├── entity.py            # Base entity definition
│   ├── repository.py        # Generic repository pattern
│   ├── specification.py     # Query specifications
│   └── db_context.py        # Database session management
│
├── infrastructure/          # Infrastructure components
│   ├── logging/            # Logging infrastructure
│   └── persistence/        # Database infrastructure
│
├── domain/                 # Domain models and business logic
│
└── utils/                  # Utility functions and helpers
```

## 🚀 Key Features

### Core Engine
- **Dependency Injection Container**: Fully featured DI container with support for:
  - Singleton, Scoped, and Transient lifetimes
  - Automatic constructor injection
  - Factory registration
  - Generic type resolution

### Startup System
- **Ordered Initialization**: Define startup tasks with dependencies
- **Configuration Integration**: Automatic configuration injection into startup tasks
- **Async Support**: Full async/await support for startup tasks
- **Auto-discovery**: Automatic discovery and registration of startup tasks

### Repository Pattern
- **Generic Repositories**: Type-safe generic repository pattern
- **Specification Pattern**: Fluent query building with specifications
- **Async Database Operations**: Full async support for database operations
- **Session Management**: Automatic session lifecycle management

### Configuration
- **Hierarchical Config**: Multi-level configuration system
- **Environment Support**: Environment variable integration
- **Type Safety**: Strong typing with dataclass validation
- **Hot Reload**: Configuration hot-reload support (where applicable)

### Infrastructure
- **Structured Logging**: Consistent logging across components
- **Database Abstraction**: Clean separation of database concerns
- **Error Handling**: Centralized error handling and logging

## 🧪 Requirements

- Python 3.9+
- SQLAlchemy
- PyYAML
- aiosqlite
- dataclasses (built-in for Python 3.9+)

## 📝 License

This library is released under the MIT License as part of the OpenBioCure initiative.
