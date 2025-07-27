import logging
from typing import Any, ClassVar, Dict

logger = logging.getLogger(__name__)


class StartupTask:
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
    def is_enabled(self) -> bool:
        """Check if the startup task is enabled."""
        return self._is_enabled

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the startup task from configuration dictionary."""
        self._config = config

        # Check if task is explicitly enabled/disabled in config
        if "enabled" in config:
            self._is_enabled = bool(config["enabled"])

    async def execute(self) -> None:
        """Execute the startup task.

        This method is an async coroutine that should be awaited.
        If a subclass doesn't need async functionality, it can still
        implement it as a regular method - it will be converted to a coroutine.
        """
        pass

    async def cleanup(self) -> None:
        """Clean up resources used by the startup task.

        This method is an async coroutine that should be awaited.
        Subclasses should override this method to clean up any resources
        they allocate during execution.
        """
        pass

    def __init_subclass__(cls, **kwargs):
        """
        Ensure that subclasses are not considered abstract.
        This prevents the class from being skipped during discovery.
        """
        super().__init_subclass__(**kwargs)
        return cls
