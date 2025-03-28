from typing import Protocol, List
from ..config.yaml_config import YamlConfig

class IStartupTask(Protocol):
    """Interface for tasks that run during application startup."""
    def execute(self) -> None: ...

class StartupTask(IStartupTask):
    """Base class for startup tasks."""
    def execute(self) -> None:
        """Execute the startup task."""
        raise NotImplementedError("Subclasses must implement execute()")

class ConfigurationStartupTask(StartupTask):
    """Startup task that loads configuration from a YAML file."""
    def __init__(self, config_file: str):
        self.config_file = config_file
    
    def execute(self) -> None:
        """Load configuration from the YAML file."""
        config = YamlConfig.get_instance()
        config.load(self.config_file)

class StartupTaskExecutor:
    """Executes startup tasks in order."""
    def __init__(self):
        self._tasks: List[IStartupTask] = []
    
    def add_task(self, task: IStartupTask) -> 'StartupTaskExecutor':
        """Add a startup task to the executor."""
        self._tasks.append(task)
        return self
    
    def execute_all(self) -> None:
        """Execute all startup tasks in order."""
        for task in self._tasks:
            task.execute()
