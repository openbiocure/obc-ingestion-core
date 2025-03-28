import pytest
from src import engine
from src.core.engine import Engine

def test_import():
    """Test that the library can be imported."""
    assert engine is not None
    assert isinstance(engine, Engine)
