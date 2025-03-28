# HerpAI-Lib

[![Makefile CI](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml/badge.svg)](https://github.com/openbiocure/HerpAI-Lib/actions/workflows/makefile.yml)

**HerpAI-Lib** is the foundational core library for the [HerpAI](https://github.com/openbiocure/HerpAI) platform. It provides shared infrastructure components, configuration management, logging utilities, database session handling, and the repository pattern used across HerpAI agents and services.

## 💬 Join the Community

Come chat with us on Discord: [HerpAI Discord Server](https://discord.com/channels/1354737744638771220/1354737744638771223)

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
pytest tests/ --cov=src --cov-report=term-missing
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
| [01_basic_todo.py](examples/01_basic_todo.py) | Basic repository pattern with a Todo entity |
| [02_yaml_config.py](examples/02_yaml_config.py) | Working with YAML configuration and dotted access |
| [03_app_config.py](examples/03_app_config.py) | Using strongly-typed dataclass configuration |
| [04_custom_startup.py](examples/04_custom_startup.py) | Creating custom startup tasks with ordering |
| [05_database_operations.py](examples/05_database_operations.py) | Advanced database operations with repositories |
| [06_autodiscovery.py](examples/06_autodiscovery.py) | Auto-discovery of startup tasks and components |
| [07_multi_config.py](examples/07_multi_config.py) | Working with multiple configuration sources |

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
