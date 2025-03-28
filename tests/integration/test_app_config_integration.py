"""Integration tests for AppConfig with database."""
import pytest
import os
from sqlalchemy import select
from src.config.dataclass_config import AppConfig, ConfigError
from tests.mocks.mock_implementations import TestEntity

@pytest.mark.asyncio
async def test_app_config_db_session(test_config_file):
    """Test getting a database session from AppConfig."""
    # Modify the test config to use SQLite
    app_config = AppConfig.load(test_config_file)
    
    # Verify database config
    assert app_config.db_config is not None
    assert app_config.db_config.dialect == "sqlite"
    
    # Get a session - this should create connection to in-memory db
    try:
        session = app_config.get_db_session()
        
        # Session should be usable
        assert session is not None
        
        # Create a table
        TestEntity.__table__.create(app_config._engine)
        
        # Use the session to insert data
        session.add(TestEntity(
            id="app-config-test",
            name="AppConfig Test Entity",
            value=123
        ))
        session.commit()
        
        # Query the entity
        result = session.execute(select(TestEntity).where(TestEntity.id == "app-config-test"))
        entity = result.scalar_one_or_none()
        
        # Verify entity
        assert entity is not None
        assert entity.name == "AppConfig Test Entity"
        assert entity.value == 123
        
        # Close session
        session.close()
    finally:
        # Clean up engine
        if app_config._engine:
            app_config._engine.dispose()

@pytest.mark.asyncio
async def test_app_config_agents(test_config_file):
    """Test agent configuration in AppConfig."""
    # Load config
    app_config = AppConfig.load(test_config_file)
    
    # Verify default model provider
    assert app_config.default_model_provider == "test-provider"
    
    # Verify agents
    assert len(app_config.agents) == 1
    assert "test-agent" in app_config.agents
    
    # Get agent
    agent = app_config.get_agent("test-agent")
    assert agent.model == "test-model"
    assert agent.cache is True
    assert agent.tags == ["test"]
    
    # Get non-existent agent (should return default)
    default_agent = app_config.get_agent("non-existent")
    assert default_agent.model_provider == "test-provider"
    assert default_agent.model == "default-model"
