"""Integration tests for Engine with actual components."""
import pytest
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.core.interfaces import IEngine
from openbiocure_corelib.data.db_context import IDbContext, DbContext
from openbiocure_corelib.config.yaml_config import YamlConfig
from tests.mocks.mock_implementations import TestEntity, MockRepository

@pytest.mark.asyncio
async def test_engine_component_resolution(initialized_engine):
    """Test resolving various components from the engine."""
    # Ensure we can resolve core components
    resolved_engine = initialized_engine.resolve(IEngine)
    assert resolved_engine is initialized_engine

@pytest.mark.asyncio
async def test_engine_repository_registration(initialized_engine):
    """Test registering and resolving a repository."""
    # Create mock repository
    test_repo = MockRepository(TestEntity)
    
    # Register with engine
    initialized_engine.register(MockRepository, test_repo)
    
    # Resolve repository
    resolved_repo = initialized_engine.resolve(MockRepository)
    assert resolved_repo is test_repo
    
    # Create an entity using the repository
    entity = TestEntity(name="Engine Test", value=42)
    created = await resolved_repo.create(entity)
    
    # Verify entity
    assert created.name == "Engine Test"
    assert created.value == 42
