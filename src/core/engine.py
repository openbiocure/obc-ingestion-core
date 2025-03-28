from typing import TypeVar, Type, Dict, Any, Optional, Callable
import logging
import inspect
import importlib
from .singleton import Singleton
from .service_collection import ServiceCollection
from .service_scope import ServiceScope
from .interfaces import IEngine, IServiceScope

# Type variable for generic methods
T = TypeVar('T')

logger = logging.getLogger(__name__)

class Engine(IEngine):
    """
    The core application engine that provides dependency injection,
    service management, and application startup coordination.
    """
    
    # Class variable to hold the singleton instance
    _instance: Optional['Engine'] = None
    
    def __init__(self):
        """Initialize a new engine instance."""
        self._services = ServiceCollection()
        self._started = False
        self._modules = set()
        self._startup_task_executor = None
    
    @classmethod
    def initialize(cls) -> 'Engine':
        """
        Initialize or get the existing Engine instance.
        
        Returns:
            The singleton Engine instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def current(self) -> 'IEngine':
        """
        Get the current Engine instance.
        
        Returns:
            The current Engine instance
        
        Raises:
            RuntimeError: If the Engine is not initialized
        """
        if Engine._instance is None:
            raise RuntimeError("Engine not initialized. Call Engine.initialize() first.")
        return Engine._instance
    
    def start(self) -> None:
        """
        Start the engine if not already started.
        This initializes all core services and runs startup tasks.
        """
        if self._started:
            return
        
        logger.info("Starting engine...")
        
        # Import startup task executor
        try:
            startup_executor_module = importlib.import_module('src.core.startup_task_executor')
            StartupTaskExecutor = getattr(startup_executor_module, 'StartupTaskExecutor')
            
            # Discover and execute startup tasks
            self._startup_task_executor = StartupTaskExecutor().discover_tasks()
            
            # Get configuration to configure tasks
            try:
                yaml_config_module = importlib.import_module('src.config.yaml_config')
                YamlConfig = getattr(yaml_config_module, 'YamlConfig')
                
                config = YamlConfig.get_instance()
                self._startup_task_executor.configure_tasks(config._config)
            except Exception as e:
                logger.warning(f"Failed to configure startup tasks from config: {str(e)}")
            
            # Execute startup tasks
            self._startup_task_executor.execute_all()
        except Exception as e:
            logger.warning(f"Failed to execute startup tasks: {str(e)}")
        
        # Register core services
        self._register_core_services()
        
        self._started = True
        logger.info("Engine started successfully")
    
    def resolve(self, type_: Type[T]) -> T:
        """
        Resolve a service from the container.
        
        Args:
            type_: The type of service to resolve
            
        Returns:
            The resolved service
            
        Raises:
            RuntimeError: If the Engine is not started
            ValueError: If the service is not registered
        """
        if not self._started:
            raise RuntimeError("Engine not started. Call start() first.")
        
        service = self._services.get_service(type_)
        if service is None:
            raise ValueError(f"No registration found for {type_.__name__}")
        return service
    
    def create_scope(self) -> IServiceScope:
        """
        Create a service scope.
        
        Returns:
            A new service scope
        """
        return ServiceScope(self)
    
    def register(self, interface_type: Type[T], implementation) -> None:
        """
        Register a singleton service.
        
        Args:
            interface_type: The interface or type to register
            implementation: The implementation type, instance, or factory
        """
        self._services.add_singleton(interface_type, implementation)
    
    def add_startup_task(self, task) -> None:
        """
        Add a startup task to be executed when the engine starts.
        
        Note: This method is not typically needed as startup tasks are auto-discovered.
        Use it only if you need to add a task dynamically.
        
        Args:
            task: The startup task to add
        """
        if self._startup_task_executor is None:
            try:
                startup_executor_module = importlib.import_module('src.core.startup_task_executor')
                StartupTaskExecutor = getattr(startup_executor_module, 'StartupTaskExecutor')
                
                self._startup_task_executor = StartupTaskExecutor()
            except Exception:
                logger.warning("StartupTaskExecutor not available")
                return
        self._startup_task_executor.add_task(task)
    
    def _register_core_services(self):
        """Register core services required by the library."""
        # Register self
        self._services.add_singleton(IEngine, self)
        self._services.add_singleton(Engine, self)
        
        # Register configuration
        try:
            yaml_config_module = importlib.import_module('src.config.yaml_config')
            YamlConfig = getattr(yaml_config_module, 'YamlConfig')
            
            config = YamlConfig.get_instance()
            self._services.add_singleton(YamlConfig, config)
        except Exception:
            logger.warning("YamlConfig not available")
        
        # Setup database using configuration
        try:
            db_context_module = importlib.import_module('src.data.db_context')
            IDbContext = getattr(db_context_module, 'IDbContext')
            DbContext = getattr(db_context_module, 'DbContext')
            
            self._services.add_singleton(IDbContext, lambda: DbContext())
            self._services.add_singleton(DbContext, lambda: self.resolve(IDbContext))
        except Exception:
            logger.warning("DbContext not available")
        
        # Auto-discover and register repositories
        self._discover_and_register_entities()
    
    def _discover_and_register_entities(self):
        """Discover entity types and register repositories for them."""
        # This would scan packages and modules to find entity types
        # Then register appropriate repositories
        # Simplified implementation
        pass
