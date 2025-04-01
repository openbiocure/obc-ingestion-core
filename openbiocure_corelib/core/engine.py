from typing import TypeVar, Type, Dict, Any, Optional, Callable, List, Set
import logging
import inspect
import sys
import importlib
from .singleton import Singleton
from .service_collection import ServiceCollection
from .service_scope import ServiceScope
from .interfaces import IEngine, IServiceScope
from .type_finder import ITypeFinder, TypeFinder
from .startup_task import StartupTask

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
        self._repository_registrations = {}
    
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
    
    @classmethod
    def current(cls) -> 'IEngine':
        """
        Get the current Engine instance.
        
        Returns:
            The current Engine instance
        
        Raises:
            RuntimeError: If the Engine is not initialized or not started
        """
        if cls._instance is None:
            raise RuntimeError("Engine not initialized. Call Engine.initialize() first.")
        
        if not cls._instance._started:
            raise RuntimeError("Engine not started. Call Engine.start() first.")
            
        return cls._instance
    
    async def start(self) -> None:
        """
        Start the engine if not already started.
        This initializes all core services and runs startup tasks.
        """
        if self._started:
            return
        
        logger.info("Starting engine...")
        
        # Register core services first
        self._register_core_services()
        
        # After all services are registered, complete repository registrations
        self._complete_repository_registrations()
        
        # Mark engine as started before executing startup tasks
        self._started = True
        
        # Execute startup tasks in a special startup scope
        try:
            from .startup_task_executor import StartupTaskExecutor
            
            # Discover and execute startup tasks
            self._startup_task_executor = StartupTaskExecutor()
            for task_class in TypeFinder().find_classes_of_type(StartupTask, only_concrete=True):
                self._startup_task_executor.add_task(task_class())
            
            # Get configuration to configure tasks
            try:
                from ..config.app_config import AppConfig
                
                config = AppConfig.get_instance()
                self._startup_task_executor.configure_tasks(config.__dict__)
            except Exception as e:
                logger.warning(f"Failed to configure startup tasks from config: {str(e)}")
            
            # Execute startup tasks asynchronously
            await self._startup_task_executor.execute_all_async()
        except Exception as e:
            logger.warning(f"Failed to execute startup tasks: {str(e)}")
            # If startup tasks fail, mark engine as not started
            self._started = False
            raise
        
        logger.info("Engine started successfully")
    
    def _complete_repository_registrations(self):
        """
        Complete repository registrations by creating factory methods
        that will resolve dependencies correctly.
        """
        for interface_type, repo_info in self._repository_registrations.items():
            repo_class = repo_info["repo_class"]
            entity_type = repo_info["entity_type"]
            
            # Use a function to capture the current values in the closure
            def create_factory(rc=repo_class, et=entity_type):
                # Return a lambda that will be called when the service is resolved
                return lambda: self._create_repository_instance(rc, et)
            
            # Store the factory function in the service collection
            factory = create_factory()
            self._services._services[interface_type] = factory
    
    def _create_repository_instance(self, repo_class, entity_type):
        """
        Create a repository instance with the necessary dependencies.
        This is called when someone resolves the repository from the container.
        """
        from sqlalchemy.ext.asyncio import AsyncSession
        
        # Try to get the database session
        session = self._services.get_service(AsyncSession)
        if not session:
            # Try getting it from DbContext
            try:
                from openbiocure_corelib.data.db_context import IDbContext
                db_context = self._services.get_service(IDbContext)
                if db_context:
                    session = db_context.session
            except Exception:
                logger.warning(f"Failed to get session from DbContext")
        
        if not session:
            # As a last resort, create a mock/in-memory session for testing/development
            logger.warning(f"Creating in-memory session for {repo_class.__name__}")
            try:
                # This is a placeholder - you may want to implement a proper in-memory session
                session = self._create_memory_session()
            except Exception as e:
                logger.error(f"Failed to create in-memory session: {str(e)}")
                raise ValueError(f"Could not resolve database session for {repo_class.__name__}")
        
        # Create and return the repository instance
        return repo_class(session, entity_type)
    
    def _create_memory_session(self):
        """
        Create an in-memory database session for development/testing.
        """
        try:
            # Import necessary modules
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import sessionmaker
            
            # Create an in-memory SQLite engine
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            
            # Create a session factory
            async_session = sessionmaker(
                bind=engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            
            # Create and return a session
            return async_session()
        except Exception as e:
            logger.error(f"Failed to create in-memory session: {str(e)}")
            raise
    
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
                startup_executor_module = importlib.import_module('openbiocure_corelib.core.startup_task_executor')
                StartupTaskExecutor = getattr(startup_executor_module, 'StartupTaskExecutor')
                
                self._startup_task_executor = StartupTaskExecutor()
            except Exception:
                logger.warning("StartupTaskExecutor not available")
                return
        self._startup_task_executor.add_task(task)
    
    def register_module(self, module_path: str) -> None:
        """
        Register a module to be scanned for repositories and other components.
        
        Args:
            module_path: The module path to scan
        """
        self._modules.add(module_path)
        
        # If the engine is already started, scan the new module immediately
        if self._started:
            try:
                # Get the type finder
                type_finder = self.resolve(ITypeFinder)
                
                # Load the module
                type_finder.load_module(module_path)
                
                # Re-scan for repositories
                self._discover_and_register_entities()
            except Exception as e:
                logger.warning(f"Error scanning module {module_path}: {str(e)}")

    def _register_core_services(self):
        """Register core services required by the library."""
        # Register self
        self._services.add_singleton(IEngine, self)
        self._services.add_singleton(Engine, self)
        
        # Register TypeFinder (NopCommerce style)
        type_finder = TypeFinder()
        self._services.add_singleton(ITypeFinder, type_finder)
        
        # Register configuration
        try:
            from openbiocure_corelib.config.app_config import AppConfig
            
            # Get or initialize app config
            app_config = AppConfig.get_instance()
            self._services.add_singleton(AppConfig, lambda: app_config)
            
            # Setup database using AppConfig
            try:
                from openbiocure_corelib.data.db_context import IDbContext, DbContext
                from sqlalchemy.ext.asyncio import AsyncSession
                
                # Check if we have a database config
                if app_config.db_config:
                    connection_string = app_config.db_config.connection_string
                    # Add async driver for SQLite if not specified
                    if app_config.db_config.dialect == "sqlite" and not app_config.db_config.driver:
                        connection_string = connection_string.replace("sqlite://", "sqlite+aiosqlite://")
                    
                    # Create DbContext with connection string from config
                    db_context = DbContext(connection_string)
                else:
                    # Create in-memory SQLite database as fallback
                    db_context = DbContext("sqlite+aiosqlite:///:memory:")
                    logger.warning("Using in-memory SQLite database as fallback")
                
                # Register DbContext and its session
                self._services.add_singleton(IDbContext, lambda: db_context)
                self._services.add_singleton(DbContext, lambda: db_context)
                
                # Also register AsyncSession directly if needed by repositories
                self._services.add_singleton(AsyncSession, lambda: db_context.session)
            except Exception as e:
                logger.warning(f"DbContext not available: {str(e)}")
                
        except Exception as e:
            logger.warning(f"AppConfig not available: {str(e)}")
        
        # Auto-discover and register repositories
        self._discover_and_register_entities()
    
    def _discover_and_register_entities(self):
        """Discover entity types and register repositories for them using TypeFinder."""
        logger.info("Discovering repositories using TypeFinder...")
        
        try:
            # Import sys if not already imported
            import sys
            
            # Get TypeFinder directly
            type_finder = self._services.get_service(ITypeFinder)
            
            if not type_finder:
                logger.warning("TypeFinder not registered, skipping repository discovery")
                return
            
            # Import the IRepository interface
            from openbiocure_corelib.data.repository import IRepository
            
            # Find all specific repository interfaces first (like ITodoRepository)
            all_modules = list(sys.modules.values())
            specific_repo_interfaces = {}  # Map interface name to interface class
            
            # Try to find specific repository interfaces
            for module in all_modules:
                if not module or not hasattr(module, "__dict__"):
                    continue
                
                try:
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if name.startswith('I') and 'Repository' in name and name != 'IRepository':
                            specific_repo_interfaces[name] = obj
                            logger.info(f"Found specific repository interface: {name}")
                except Exception:
                    pass
            
            logger.info(f"Found {len(specific_repo_interfaces)} specific repository interfaces")
            
            # Find all generic implementations of IRepository<T>
            repository_implementations = type_finder.find_generic_implementations(IRepository)
            logger.info(f"Found {len(repository_implementations)} repository implementations")
            
            # Look for concrete entity types in modules
            entity_types = {}
            for module in all_modules:
                if not module or not hasattr(module, "__dict__"):
                    continue
                
                try:
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Check if it's an entity class (e.g., Todo)
                        # You might want to add more specific criteria here
                        if not name.startswith('I') and not name.endswith('Repository'):
                            entity_types[name] = obj
                except Exception:
                    pass
            
            # Find actual implementation for each repository interface
            for repo_class, type_args in repository_implementations:
                # Register the generic repository
                if type_args:
                    entity_type = type_args[0]
                    generic_interface = IRepository[entity_type]
                    
                    # Create and register the generic repository
                    def create_generic_factory(rc=repo_class, et=entity_type):
                        return lambda: self._create_repository_instance(rc, et)
                    
                    self._services._services[generic_interface] = create_generic_factory()
                    logger.info(f"Registered generic interface IRepository<{entity_type.__name__}> with {repo_class.__name__}")
                    
                    # Now try to register specific interfaces
                    for interface_name, interface_class in specific_repo_interfaces.items():
                        # Extract entity name from interface (e.g., ITodoRepository -> Todo)
                        extracted_name = None
                        if interface_name.startswith('I') and interface_name.endswith('Repository'):
                            extracted_name = interface_name[1:-10]
                        
                        # Now check if this extracted name matches a known entity type
                        if extracted_name and extracted_name in entity_types:
                            actual_entity_type = entity_types[extracted_name]
                            logger.info(f"Matching interface {interface_name} with entity {extracted_name}")
                            
                            # Create and register the specific repository implementation
                            def create_specific_factory(rc=repo_class, et=actual_entity_type):
                                return lambda: self._create_repository_instance(rc, et)
                            
                            self._services._services[interface_class] = create_specific_factory()
                            logger.info(f"Registered specific interface {interface_name} with {repo_class.__name__}")
        
        except Exception as e:
            logger.error(f"Error during repository discovery: {str(e)}", exc_info=True)