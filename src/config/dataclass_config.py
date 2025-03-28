import yaml
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass

@dataclass
class DatabaseConfig:
    """Database configuration parameters"""
    host: str
    port: int
    database: str
    username: str
    password: str
    dialect: str = "postgresql"
    driver: str = "psycopg2"

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string"""
        return f"{self.dialect}+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'DatabaseConfig':
        """Create DatabaseConfig from dictionary"""
        required_fields = {'host', 'port', 'database', 'username', 'password'}
        missing_fields = required_fields - set(config.keys())
        
        if missing_fields:
            raise ConfigError(f"Missing required database configuration fields: {missing_fields}")
        
        return cls(
            host=config['host'],
            port=int(config['port']),
            database=config['database'],
            username=config['username'],
            password=config['password'],
            dialect=config.get('dialect', 'postgresql'),
            driver=config.get('driver', 'psycopg2')
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
    def from_dict(cls, config: Dict[str, Any], default_provider: str) -> 'AgentConfig':
        """Create AgentConfig from dictionary"""
        if 'model' not in config:
            raise ConfigError(f"Missing required field 'model' in agent configuration")
        
        return cls(
            model_provider=config.get('model_provider', default_provider),
            model=config['model'],
            prompt_version=config.get('prompt_version', 'v1'),
            cache=config.get('cache', False),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.5),
            tags=config.get('tags', []),
            is_research_domain=config.get('is_research_domain', False)
        )

@dataclass
class AppConfig:
    """Application configuration container"""
    default_model_provider: str
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    db_config: Optional[DatabaseConfig] = None
    _engine: Optional[Engine] = None
    _session_maker: Optional[sessionmaker] = None
    
    # Singleton pattern
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'AppConfig':
        """Get the singleton instance of AppConfig."""
        if cls._instance is None:
            cls._instance = cls.load()
        return cls._instance

    @classmethod
    def load(cls, path: str = "config.yaml") -> 'AppConfig':
        """Load configuration from YAML file"""
        try:
            config_path = Path(path)
            if not config_path.exists():
                raise ConfigError(f"Configuration file not found: {path}")

            with open(config_path) as f:
                raw_cfg = yaml.safe_load(f)

            if not isinstance(raw_cfg, dict):
                raise ConfigError("Invalid YAML configuration format")

            app_cfg = raw_cfg.get('app', {})
            if not app_cfg:
                raise ConfigError("Missing 'app' section in configuration")

            if 'default_model_provider' not in app_cfg:
                raise ConfigError("Missing 'default_model_provider' in app configuration")

            # Initialize database configuration
            db_config = None
            if 'database' in raw_cfg:
                db_config = DatabaseConfig.from_dict(raw_cfg['database'])

            # Initialize agent configurations
            agents_cfg = {}
            for name, agent_cfg in app_cfg.get('agents', {}).items():
                try:
                    agents_cfg[name] = AgentConfig.from_dict(
                        agent_cfg, 
                        app_cfg['default_model_provider']
                    )
                except ConfigError as e:
                    raise ConfigError(f"Error in agent '{name}' configuration: {str(e)}")

            return cls(
                default_model_provider=app_cfg['default_model_provider'],
                agents=agents_cfg,
                db_config=db_config
            )

        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML configuration: {str(e)}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {str(e)}")

    def get_agent(self, agent_name: str) -> AgentConfig:
        """Get agent configuration by name"""
        if agent_name not in self.agents:
            return AgentConfig(
                model_provider=self.default_model_provider,
                model="default-model"
            )
        return self.agents[agent_name]

    def get_db_session(self) -> Session:
        """Get database session with lazy initialization"""
        if not self.db_config:
            raise ConfigError("Database configuration not set")

        try:
            # Create engine if it doesn't exist
            if not self._engine:
                self._engine = create_engine(
                    self.db_config.connection_string,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10
                )

            # Create session maker if it doesn't exist
            if not self._session_maker:
                self._session_maker = sessionmaker(
                    bind=self._engine,
                    expire_on_commit=False
                )

            return self._session_maker()

        except Exception as e:
            raise ConfigError(f"Error creating database session: {str(e)}")
