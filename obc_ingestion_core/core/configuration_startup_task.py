import importlib
import logging

from .startup_task import StartupTask

logger = logging.getLogger(__name__)


class ConfigurationStartupTask(StartupTask):
    """Startup task that loads configuration from a YAML file."""

    # Run very early
    order = 10

    async def execute(self) -> None:
        """Load configuration from the YAML file."""
        try:
            # Lazy import to avoid circular dependencies
            yaml_config_module = importlib.import_module(
                "obc_ingestion_core.config.yaml_config"
            )
            YamlConfig = getattr(yaml_config_module, "YamlConfig")

            config_path = self._config.get("path", "config.yaml")
            config = YamlConfig.get_instance()
            config.load(config_path)
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
