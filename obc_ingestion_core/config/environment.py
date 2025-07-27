import os
from typing import Optional


class Environment:
    """Helper for accessing environment variables."""

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an environment variable value."""
        return os.environ.get(key, default)

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get an environment variable as a boolean."""
        value = os.environ.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "yes", "1", "on")

    @staticmethod
    def get_int(key: str, default: Optional[int] = None) -> Optional[int]:
        """Get an environment variable as an integer."""
        value = os.environ.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
