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
