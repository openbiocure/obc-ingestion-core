import os
from typing import Any, Dict, List, Optional, cast

import yaml


class YamlConfig:
    """Configuration manager for YAML-based configuration."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "YamlConfig":
        """Get the singleton instance of YamlConfig."""
        if cls._instance is None:
            cls._instance = YamlConfig()
        return cls._instance

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._loaded_files: List[str] = []

    def load(self, config_file: str) -> None:
        """Load configuration from a YAML file."""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            self._config.update(config)

        self._loaded_files.append(config_file)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.

        Key can be a dot-separated path (e.g., 'database.host').
        """
        parts = key.split(".")
        value = self._config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def get_connection_string(self) -> str:
        """Generate a database connection string from the configuration."""
        db_config = self.get("database", {})

        dialect = db_config.get("dialect", "sqlite")
        driver = db_config.get("driver", "")

        if dialect == "sqlite":
            database = db_config.get("database", "openbiocure-catalog")
            return f"sqlite+aiosqlite:///{database}"

        driver_str = f"+{driver}" if driver else ""
        host = db_config.get("host", "localhost")
        port = db_config.get("port", "")
        port_str = f":{port}" if port else ""
        database = db_config.get("database", "")
        username = db_config.get("username", "")
        password = db_config.get("password", "")

        auth_str = ""
        if username:
            auth_str = f"{username}"
            if password:
                auth_str += f":{password}"
            auth_str += "@"

        return f"{dialect}{driver_str}://{auth_str}{host}{port_str}/{database}"

    def get_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent configurations."""
        return cast(Dict[str, Dict[str, Any]], self.get("app.agents", {}))

    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent."""
        return cast(Optional[Dict[str, Any]], self.get(f"app.agents.{agent_name}"))
