from .startup import StartupTask
from ..config.dataclass_config import AppConfig

class AppConfigStartupTask(StartupTask):
    """Startup task for loading AppConfig."""
    
    # Run early in the startup sequence
    order = 20
    
    def execute(self) -> None:
        """Load AppConfig from the YAML file."""
        config_path = self._config.get('path', 'config.yaml')
        AppConfig.load(config_path)
