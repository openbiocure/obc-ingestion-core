import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Callable

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Base exception for configuration errors"""

    pass


@dataclass
class DatabaseConfig:
    """Database configuration parameters"""

    dialect: str = "sqlite"
    driver: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = "openbiocure-catalog.db"
    username: Optional[str] = None
    password: Optional[str] = None
    is_memory_db: bool = False
    _connection_string: Optional[str] = None

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string"""
        if self._connection_string:
            return self._connection_string

        if self.dialect == "sqlite":
            driver_part = f"+{self.driver}" if self.driver else ""
            if self.is_memory_db:
                return f"sqlite{driver_part}:///:memory:"
            return f"sqlite{driver_part}:///{self.database}"
        else:
            return f"{self.dialect}+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "DatabaseConfig":
        """Create DatabaseConfig from dictionary"""
        # If connection_string is provided, use it directly
        if "connection_string" in config:
            return cls(
                dialect="sqlite",
                driver=config.get("driver", "aiosqlite"),
                is_memory_db=config.get("is_memory_db", True),
                _connection_string=config["connection_string"],
            )

        dialect = config.get("dialect", "sqlite")

        # For SQLite, we need different validation
        if dialect == "sqlite":
            # Default to memory DB if no database path provided
            is_memory_db = config.get("is_memory_db", False)
            database = config.get("database", "herpai.db") if not is_memory_db else None

            return cls(
                dialect="sqlite",
                driver=config.get("driver"),
                database=database,
                is_memory_db=is_memory_db,
            )
        else:
            # For other databases like PostgreSQL, validate required fields
            required_fields = {"host", "port", "database", "username", "password"}
            missing_fields = required_fields - set(config.keys())

            if missing_fields:
                raise ConfigError(
                    f"Missing required database configuration fields: {missing_fields}"
                )

            return cls(
                dialect=dialect,
                driver=config.get("driver", "psycopg2"),
                host=config["host"],
                port=int(config["port"]),
                database=config["database"],
                username=config["username"],
                password=config["password"],
            )


@dataclass
class AgentConfig:
    """Agent-specific configuration"""

    model_provider: str
    model: str
    prompt_version: str = "v1"
    cache: bool = False
    max_tokens: int = 1000
    temperature: float = 0.5
    tags: List[str] = field(default_factory=list)
    is_research_domain: bool = False

    @classmethod
    def from_dict(cls, config: Dict[str, Any], default_provider: str) -> "AgentConfig":
        """Create AgentConfig from dictionary"""
        if "model" not in config:
            raise ConfigError("Missing required field 'model' in agent configuration")

        return cls(
            model_provider=config.get("model_provider", default_provider),
            model=config["model"],
            prompt_version=config.get("prompt_version", "v1"),
            cache=config.get("cache", False),
            max_tokens=config.get("max_tokens", 1000),
            temperature=config.get("temperature", 0.5),
            tags=config.get("tags", []),
            is_research_domain=config.get("is_research_domain", False),
        )


@dataclass
class AppConfig:
    """Application configuration container"""

    default_model_provider: str = "claude"
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    db_config: Optional[DatabaseConfig] = None
    _engine: Optional[Engine] = None
    _session_maker: Optional[Callable[[], Session]] = None

    # Singleton pattern
    _instance = None

    @classmethod
    def get_instance(cls) -> "AppConfig":
        """Get the singleton instance of AppConfig."""
        if cls._instance is None:
            try:
                cls._instance = cls.load()
                logger.info("AppConfig loaded successfully")
            except Exception as e:
                logger.warning(
                    f"Error loading configuration: {str(e)}. Using default values."
                )
                # Create default instance with in-memory SQLite database
                cls._instance = cls(
                    default_model_provider="claude",
                    db_config=DatabaseConfig(is_memory_db=True),
                )
        return cls._instance

    @classmethod
    def load(cls, path: str = "config.yaml") -> "AppConfig":
        """Load configuration from YAML file"""
        try:
            config_path = Path(path)
            if not config_path.exists():
                logger.warning(
                    f"Configuration file not found: {path}. Using default configuration."
                )
                return cls(
                    default_model_provider="claude",
                    db_config=DatabaseConfig(is_memory_db=True),
                )

            with open(config_path) as f:
                raw_cfg = yaml.safe_load(f)

            if not isinstance(raw_cfg, dict):
                raise ConfigError("Invalid YAML configuration format")
            app_cfg = raw_cfg.get("app", {})
            if not app_cfg:
                logger.warning(
                    "Missing 'app' section in configuration, defaulting to empty dictionary"
                )
                app_cfg = {}

            default_provider = app_cfg.get("default_model_provider", "claude")

            # Initialize database configuration
            db_config = None
            if "database" in raw_cfg:
                db_config = DatabaseConfig.from_dict(raw_cfg["database"])
            else:
                # Create default SQLite database config
                db_config = DatabaseConfig(is_memory_db=True)
                logger.info(
                    "No database configuration found, using in-memory SQLite database"
                )

            # Initialize agent configurations
            agents_cfg = {}
            for name, agent_cfg in app_cfg.get("agents", {}).items():
                try:
                    agents_cfg[name] = AgentConfig.from_dict(
                        agent_cfg, default_provider
                    )
                except ConfigError as e:
                    logger.warning(f"Error in agent '{name}' configuration: {str(e)}")

            return cls(
                default_model_provider=default_provider,
                agents=agents_cfg,
                db_config=db_config,
            )

        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML configuration: {str(e)}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {str(e)}")

    def get_agent(self, agent_name: str) -> AgentConfig:
        """Get agent configuration by name"""
        if agent_name not in self.agents:
            # Return default agent if specific agent not found
            return AgentConfig(
                model_provider=self.default_model_provider,
                model="claude-3-7-sonnet-latest",
            )
        return self.agents[agent_name]

    def get_db_session(self) -> Session:
        """Get database session with lazy initialization"""
        if not self.db_config:
            # Create default in-memory database if none exists
            self.db_config = DatabaseConfig(is_memory_db=True)
            logger.warning(
                "No database configuration. Using in-memory SQLite database."
            )

        try:
            # Create engine if it doesn't exist
            if not self._engine:
                self._engine = create_engine(
                    self.db_config.connection_string,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10,
                )

            # Create session maker if it doesn't exist
            if not self._session_maker:
                self._session_maker = sessionmaker(
                    bind=self._engine, expire_on_commit=False
                )

            return self._session_maker()

        except Exception as e:
            logger.error(f"Error creating database session: {str(e)}")
            raise ConfigError(f"Error creating database session: {str(e)}")
