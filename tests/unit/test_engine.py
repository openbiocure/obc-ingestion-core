import pytest
from src import engine
from src.core.engine import Engine
from src.core.dependency import IEngine

def test_engine_singleton():
    # Test that engine.initialize() always returns the same instance
    instance1 = Engine.initialize()
    instance2 = Engine.initialize()
    assert instance1 is instance2
    
    # Test that engine exported from src is also the same instance
    assert engine is instance1

def test_engine_resolve(initialized_engine):
    # Test that the engine can resolve itself
    resolved_engine = initialized_engine.resolve(IEngine)
    assert resolved_engine is initialized_engine
