from .core.engine import Engine

# Export the Engine as a singleton for convenient access
engine = Engine.initialize()

__all__ = ['engine']
