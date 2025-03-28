from typing import Protocol, List, Dict, Type, Set, Optional, ClassVar
import inspect
import importlib
import pkgutil
import sys
from pathlib import Path
from abc import ABC, abstractmethod
import logging

from ..config.yaml_config import YamlConfig

logger = logging.getLogger(__name__)

class IStartupTask(Protocol):
    """Interface for tasks that run during application startup."""
    @property
    def order(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def enabled(self) -> bool: ...
    
    def configure(self, config: Dict) -> None: ...
    def execute(self) -> None: ...

class StartupTask(ABC):
    """Base class for startup tasks."""
    
    # Class variables to define behavior
    order: ClassVar[int] = 100  # Default order (higher runs later)
    enabled: ClassVar[bool] = True  # Default enabled state
    
    def __init__(self):
        self._config: Dict = {}
        self._is_enabled = self.__class__.enabled
    
    @property
    def name(self) -> str:
        """Get the name of the startup task."""
        return self.__class__.__name__
    
    @property
    def order(self) -> int:
        """Get the order of the startup task."""
        return self.__class__.order
    
    @property
    def enabled(self) -> bool:
        """Check if the startup task is enabled."""
        return self._is_enabled
    
    def configure(self, config: Dict) -> None:
        """Configure the startup task from configuration dictionary."""
        self._config = config
        
        # Check if task is explicitly enabled/disabled in config
        if 'enabled' in config:
            self._is_enabled = bool(config['enabled'])
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the startup task."""
        pass

class ConfigurationStartupTask(StartupTask):
    """Startup task that loads configuration from a YAML file."""
    order = 10  # Run very early
    
    def execute(self) -> None:
        """Load configuration from the YAML file."""
        config_path = self._config.get('path', 'config.yaml')
        config = YamlConfig.get_instance()
        try:
            config.load(config_path)
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise

class StartupTaskExecutor:
    """Executes startup tasks in order."""
    def __init__(self):
        self._tasks: Dict[str, IStartupTask] = {}
        self._task_config: Dict[str, Dict] = {}
    
    def add_task(self, task: IStartupTask) -> 'StartupTaskExecutor':
        """Add a startup task to the executor."""
        self._tasks[task.name] = task
        return self
    
    def configure_tasks(self, config: Dict) -> None:
        """Configure tasks from a configuration dictionary."""
        self._task_config = config.get('startup_tasks', {})
        
        # Configure all tasks
        for name, task in self._tasks.items():
            task_config = self._task_config.get(name, {})
            task.configure(task_config)
    
    def execute_all(self) -> None:
        """Execute all enabled startup tasks in order."""
        # Sort tasks by order
        sorted_tasks = sorted(
            [task for task in self._tasks.values() if task.enabled], 
            key=lambda t: t.order
        )
        
        # Execute tasks
        for task in sorted_tasks:
            logger.info(f"Executing startup task: {task.name}")
            task.execute()

    @classmethod
    def discover_tasks(cls) -> 'StartupTaskExecutor':
        """Discover all startup tasks in the application."""
        executor = cls()
        discovered_tasks: Set[Type[StartupTask]] = set()
        
        # Find all subclasses of StartupTask
        def find_tasks_in_module(module_name):
            try:
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj) 
                        and issubclass(obj, StartupTask) 
                        and obj != StartupTask
                        and obj not in discovered_tasks
                    ):
                        discovered_tasks.add(obj)
                        executor.add_task(obj())
            except Exception as e:
                logger.warning(f"Error discovering tasks in module {module_name}: {str(e)}")
        
        # Search in core, config, and application packages
        base_packages = ['src.core', 'src.config']
        
        # Add application-specific packages if specified
        try:
            import src
            if hasattr(src, '__packages__'):
                base_packages.extend(src.__packages__)
        except ImportError:
            pass
        
        # Discover tasks in packages
        for package_name in base_packages:
            try:
                package = importlib.import_module(package_name)
                find_tasks_in_module(package_name)
                
                # Also check submodules
                if hasattr(package, '__path__'):
                    for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                        find_tasks_in_module(name)
            except ImportError:
                logger.warning(f"Package {package_name} not found, skipping task discovery")
        
        logger.info(f"Discovered {len(discovered_tasks)} startup tasks")
        return executor
