from typing import Dict, ClassVar, Any
from abc import ABC, abstractmethod

class StartupTask(ABC):
    """Base class for startup tasks."""
    
    # Class variables to define behavior
    order: ClassVar[int] = 100  # Default order (higher runs later)
    enabled: ClassVar[bool] = True  # Default enabled state
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
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
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the startup task from configuration dictionary."""
        self._config = config
        
        # Check if task is explicitly enabled/disabled in config
        if 'enabled' in config:
            self._is_enabled = bool(config['enabled'])
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the startup task."""
        pass
