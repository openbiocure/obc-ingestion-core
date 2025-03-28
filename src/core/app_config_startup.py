from ..core.startup import StartupTask
from ..config.dataclass_config import AppConfig

class AppConfigStartupTask(StartupTask):
    """Startup task for loading AppConfig."""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
    
    def execute(self) -> None:
        """Load AppConfig from the YAML file."""
        AppConfig.load(self.config_file)
