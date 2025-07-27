import json
import os
from typing import Any, Dict, Optional


class Settings:
    def __init__(self, settings_file: Optional[str] = None):
        self._settings: Dict[str, Any] = {}
        if settings_file and os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                self._settings = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings[key] = value

    def save(self, settings_file: str) -> None:
        """Save settings to a file."""
        with open(settings_file, "w") as f:
            json.dump(self._settings, f, indent=2)
