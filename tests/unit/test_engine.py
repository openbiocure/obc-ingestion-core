"""Tests for the Engine module."""

import pytest

from openbiocure_corelib.core.engine import Engine


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
async def test_engine_property(initialized_engine):
    """Test that the current property returns the engine instance."""
    assert Engine.current() is initialized_engine


@pytest.mark.asyncio
async def test_engine_start(test_config_file):
    """Test that the engine can be started."""
    # Reset engine state
    Engine._instance = None

    # Set config file path
    import os

    os.environ["CONFIG_FILE"] = test_config_file

    # Create a test engine with no auto-discovery
    test_engine = Engine.initialize()

    # Start with no failures
    await test_engine.start()

    # Verify started
    assert test_engine._started is True

    # Clean up
    await test_engine.stop()
    Engine._instance = None
    if "CONFIG_FILE" in os.environ:
        del os.environ["CONFIG_FILE"]


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
