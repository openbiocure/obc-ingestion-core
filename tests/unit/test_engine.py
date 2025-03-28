"""Tests for the Engine module."""
import pytest
from src.core.engine import Engine
from src.core.interfaces import IEngine

def test_engine_singleton():
    """Test that the engine uses the singleton pattern."""
    # Reset the singleton first
    Engine._instance = None
    
    # Initialize twice, should get same instance
    engine1 = Engine.initialize()
    engine2 = Engine.initialize()
    
    assert engine1 is engine2
    
    # For the next test
    Engine._instance = None

def test_engine_property():
    """Test that the current property returns the engine instance."""
    test_engine = Engine.initialize()
    assert test_engine.current is test_engine
    
    # For the next test
    Engine._instance = None

def test_engine_register_resolve():
    """Test registering and resolving services."""
    # Create a test engine
    test_engine = Engine()
    test_engine._started = True  # Mark as started for testing
    
    # Create a test service
    class TestService:
        pass
    
    service = TestService()
    
    # Register service
    test_engine.register(TestService, service)
    
    # Resolve the service
    resolved = test_engine.resolve(TestService)
    
    assert resolved is service
