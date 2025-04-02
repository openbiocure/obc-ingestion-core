"""Tests for the Engine module."""
import pytest
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.core.interfaces import IEngine

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

@pytest.mark.asyncio
async def test_engine_property():
    """Test that the current property returns the engine instance."""
    test_engine = Engine.initialize()
    await test_engine.start()
    assert Engine.current() is test_engine
    
    # For the next test
    Engine._instance = None

@pytest.mark.asyncio
async def test_engine_start():
    """Test that the engine can be started."""
    # Create a test engine with no auto-discovery
    test_engine = Engine.initialize()
    
    # Start with no failures
    await test_engine.start()
    
    # Verify started
    assert test_engine._started is True
    
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
