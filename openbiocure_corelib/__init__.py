from .core.engine import Engine

# Export the Engine singleton for convenient access
engine = Engine.initialize()

__all__ = ['engine']
