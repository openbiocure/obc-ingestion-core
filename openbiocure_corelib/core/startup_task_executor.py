from typing import Dict, List, Type, Set, Optional
import inspect
import importlib
import pkgutil
import sys
import logging
import asyncio
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
    
    async def execute_all_async(self) -> None:
        """Execute all enabled startup tasks in order asynchronously."""
        # Sort tasks by order
        sorted_tasks = sorted(
            [task for task in self._tasks.values() if task.enabled], 
            key=lambda t: t.order
        )
        
        # Execute tasks
        for task in sorted_tasks:
            logger.info(f"Executing startup task: {task.name}")
            await task.execute()
    
    def execute_all(self) -> None:
        """Execute all enabled startup tasks in order."""
        import asyncio
        
        # Sort tasks by order
        sorted_tasks = sorted(
            [task for task in self._tasks.values() if task.enabled], 
            key=lambda t: t.order
        )
        
        # Create a single async function to run all tasks
        async def run_all_tasks():
            for task in sorted_tasks:
                logger.info(f"Executing startup task: {task.name}")
                await task.execute()
        
        # Run all tasks in a new event loop
        try:
            # Create a new event loop for running the tasks
            # This avoids issues with nested event loops
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            
            try:
                new_loop.run_until_complete(run_all_tasks())
            finally:
                new_loop.close()
                
        except Exception as e:
            logger.error(f"Error executing startup tasks: {str(e)}")
            raise

    def discover_tasks(self) -> 'StartupTaskExecutor':
        """
        Discover all startup tasks in the application.
        """
        # Add logging to show exactly what's happening
        logger.info("Starting startup task discovery")
        
        # Directly use TypeFinder as a local import to avoid circular dependencies
        from .type_finder import TypeFinder
        
        # Create a TypeFinder
        type_finder = TypeFinder()
        
        # Find all concrete implementations of StartupTask
        startup_task_classes = type_finder.find_classes_of_type(StartupTask, only_concrete=True)
        
        logger.info(f"Total startup task classes found: {len(startup_task_classes)}")
        
        # Log details about found classes and sort them by order
        sorted_classes = sorted(startup_task_classes, key=lambda cls: cls.order)
        
        # Log details about found classes
        for task_class in sorted_classes:
            logger.info(f"Discovered startup task class: {task_class.__name__}")
            logger.info(f"  Module: {task_class.__module__}")
            logger.info(f"  Order: {task_class.order}")
            logger.info(f"  Enabled: {task_class.enabled}")
        
        # Add discovered tasks to the executor in order
        for task_class in sorted_classes:
            try:
                task_instance = task_class()
                self.add_task(task_instance)
                logger.info(f"Added startup task: {task_class.__name__} (Order: {task_class.order})")
            except Exception as e:
                logger.error(f"Error creating startup task {task_class.__name__}: {str(e)}")
        
        return self