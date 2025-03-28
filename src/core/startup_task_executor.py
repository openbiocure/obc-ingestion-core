from typing import Dict, List, Type, Set, Optional
import inspect
import importlib
import pkgutil
import sys
import logging
from .startup_task import StartupTask

logger = logging.getLogger(__name__)

class StartupTaskExecutor:
    """Executes startup tasks in order."""
    
    def __init__(self):
        self._tasks = {}
        self._task_config = {}
    
    def add_task(self, task: StartupTask) -> 'StartupTaskExecutor':
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

    def discover_tasks(self) -> 'StartupTaskExecutor':
        """Discover all startup tasks in the application."""
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
                        self.add_task(obj())
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
        return self
