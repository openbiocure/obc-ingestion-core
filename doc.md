# OpenBioCure CoreLib API Documentation

| Module | Class | Class Description | Method | Method Description |
|---------|--------|------------------|--------|--------------------|
| `openbiocure_corelib.data.repository` | `IRepository` | *No docstring* | *various* | *See source* |
| `openbiocure_corelib.data.repository` | `Repository` | *No docstring* | *various* | *See source* |
| `openbiocure_corelib.data.entity` | `BaseEntity` | *No docstring* | *various* | *See source* |
| `openbiocure_corelib.data.specification` | `ISpecification` | *No docstring* | `is_satisfied_by` | *Inline implementation* |
| `openbiocure_corelib.data.specification` | `Specification` | *No docstring* | `is_satisfied_by` | Default implementation |
|  |  |  | `to_expression` | Convert to SQLAlchemy expression |
|  |  |  | `and_` | Combine with AND |
|  |  |  | `or_` | Combine with OR |
| `openbiocure_corelib.data.specification` | `AndSpecification` | *No docstring* | `__init__` | Initialize with two specs |
|  |  |  | `is_satisfied_by` | Logical AND of specs |
|  |  |  | `to_expression` | SQLAlchemy AND expression |
| `openbiocure_corelib.data.specification` | `OrSpecification` | *No docstring* | `__init__` | Initialize with two specs |
|  |  |  | `is_satisfied_by` | Logical OR of specs |
|  |  |  | `to_expression` | SQLAlchemy OR expression |
| `openbiocure_corelib.data.db_context` | `IDbContext` | Database context interface | *various* | *See source* |
| `openbiocure_corelib.data.db_context` | `DbContext` | Async SQLAlchemy context | `session` | Get current session |
|  |  |  | `__init__` | Initialize DbContext |
|  |  |  | `_initialize_sync` | Sync init |
|  |  |  | `session` (static) | Get current session |
| `openbiocure_corelib.config.app_config` | `ConfigError` | Base exception for configuration errors | *None* | *None* |
| `openbiocure_corelib.config.app_config` | `DatabaseConfig` | Database configuration parameters | `connection_string` | Generate SQLAlchemy connection string |
|  |  |  | `from_dict` | Create from dict |
| `openbiocure_corelib.config.app_config` | `AgentConfig` | Agent-specific configuration | `from_dict` | Create from dict |
| `openbiocure_corelib.config.app_config` | `AppConfig` | Application configuration container | `get_instance` | Singleton accessor |
|  |  |  | `load` | Load from YAML |
|  |  |  | `get_agent` | Get agent config |
|  |  |  | `get_db_session` | Get DB session |
| `openbiocure_corelib.config.environment` | `Environment` | Helper for environment variables | `get` | Get env var |
|  |  |  | `get_bool` | Get env var as bool |
|  |  |  | `get_int` | Get env var as int |
| `openbiocure_corelib.config.yaml_config` | `YamlConfig` | YAML-based config manager | `get_instance` | Singleton accessor |
|  |  |  | `__init__` | Initialize |
|  |  |  | `load` | Load YAML config |
|  |  |  | `get` | Get config value |
|  |  |  | `get_connection_string` | Generate DB connection string |
|  |  |  | `get_agent_configs` | Get all agent configs |
|  |  |  | `get_agent_config` | Get specific agent config |
| `openbiocure_corelib.config.settings` | `Settings` | *No docstring* | `__init__` | Initialize |
|  |  |  | `get` | Get setting |
|  |  |  | `set` | Set setting |
|  |  |  | `save` | Save settings |
| `openbiocure_corelib.core.service_collection` | `ServiceCollection` | *No docstring* | `__init__` | Initialize |
|  |  |  | `add_singleton` | Register singleton |
|  |  |  | `add_scoped` | Register scoped |
|  |  |  | `add_transient` | Register transient |
|  |  |  | `get_service` | Get service |
| `openbiocure_corelib.core.singleton` | `Singleton` | *No docstring* | `get_instance` | Get singleton instance |
| `openbiocure_corelib.core.type_finder` | `ITypeFinder` | Interface for finding types | `find_classes_of_type` | Find classes |
|  |  |  | `find_generic_implementations` | Find generic impls |
| `openbiocure_corelib.core.type_finder` | `TypeFinder` | *No docstring* | `__init__` | Initialize |
|  |  |  | `_is_likely_startup_module` | Check startup module |
|  |  |  | `_scan_loaded_modules` | Scan modules |
|  |  |  | `load_module` | Load module |
|  |  |  | `find_classes_of_type` | Find classes |
|  |  |  | `find_generic_implementations` | Find generic impls |
|  |  |  | `_is_assignable_to` | Check assignability |
| `openbiocure_corelib.core.engine` | `Engine` | *No docstring* | `__init__` | Initialize engine |
|  |  |  | `config` | Get config |
|  |  |  | `initialize` | Initialize singleton |
|  |  |  | `current` | Get current engine |
|  |  |  | `_complete_repository_registrations` | Register repos |
|  |  |  | `_create_repository_instance` | Create repo instance |
|  |  |  | `_create_memory_session` | Create memory session |
|  |  |  | `resolve` | Resolve service |
|  |  |  | `create_scope` | Create scope |
|  |  |  | `register` | Register service |
|  |  |  | `add_startup_task` | Add startup task |
|  |  |  | `register_module` | Register module |
|  |  |  | `_register_core_services` | Register core services |
|  |  |  | `_discover_and_register_entities` | Discover entities |
| `openbiocure_corelib.core.service_scope` | `ServiceScope` | *No docstring* | `__init__` | Initialize scope |
|  |  |  | `resolve` | Resolve service |
| `openbiocure_corelib.core.configuration_startup_task` | `ConfigurationStartupTask` | Loads YAML config | *various* | *See source* |
| `openbiocure_corelib.data.db_context_startup_task` | `DatabaseSchemaStartupTask` | Creates DB schema | *various* | *See source* |
| `openbiocure_corelib.core.startup_task` | `StartupTask` | Base class for startup tasks | `__init__` | Initialize |
|  |  |  | `name` | Name of task |
|  |  |  | `enabled` | Enabled status |
|  |  |  | `configure` | Configure task |
|  |  |  | `__init_subclass__` | Subclass hook |
| `openbiocure_corelib.core.startup_task_executor` | `StartupTaskExecutor` | Executes startup tasks | `__init__` | Initialize |
|  |  |  | `add_task` | Add task |
|  |  |  | `configure_tasks` | Configure tasks |
|  |  |  | `execute_all` | Execute tasks |
|  |  |  | `discover_tasks` | Discover tasks |
| `openbiocure_corelib.core.interfaces` | `IServiceScope` | Interface for service scope | *various* | *See source* |
|  |  |  | `IEngine` | Interface for engine | *various* | *See source* |
