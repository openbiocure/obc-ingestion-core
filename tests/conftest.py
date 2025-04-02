"""Pytest fixtures for HerpAI-Lib tests."""
import pytest
import asyncio
import os
import sys
from pathlib import Path
import tempfile
import yaml
from sqlalchemy import text

# Add parent directory to path to make openbiocure_corelib importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.core.interfaces import IEngine
from openbiocure_corelib.core.startup_task import StartupTask
from openbiocure_corelib.data.db_context import DbContext, IDbContext
from openbiocure_corelib.data.entity import BaseEntity
from tests.mocks.mock_implementations import TestEntity, MockRepository

# We'll use pytest-asyncio's built-in event_loop fixture instead of defining our own
# This avoids the deprecation warning

# Check if we're running in CI
def is_ci_environment():
    """Check if we're running in a CI environment."""
    return os.environ.get('CI') is not None or os.environ.get('GITHUB_ACTIONS') is not None

@pytest.fixture(scope="session")
def test_db_dir():
    """Create a temporary directory for test database files."""
    if is_ci_environment():
        # In CI, we'll use a dummy directory since we'll use in-memory databases
        yield "/tmp/test_db"
    else:
        # In local development, use a real temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            db_dir = Path(temp_dir) / "db"
            db_dir.mkdir(exist_ok=True)
            yield str(db_dir)

# Test configuration fixture
@pytest.fixture(scope="session")
def test_config_file(test_db_dir):
    """Create a temporary test configuration file."""
    # Configure database settings based on environment
    if is_ci_environment():
        # In CI, use in-memory SQLite database
        database_config = {
            "dialect": "sqlite",
            "driver": "aiosqlite",
            "is_memory_db": True,
            "database": None,  # Not needed for in-memory database
            "connection_string": "sqlite+aiosqlite:///:memory:"
        }
    else:
        # In local development, use file-based database
        db_path = os.path.join(test_db_dir, "test.db")
        database_config = {
            "dialect": "sqlite",
            "driver": "aiosqlite",
            "is_memory_db": False,
            "database": db_path,
            "connection_string": None
        }
    
    test_config = {
        "app": {
            "default_model_provider": "test-provider",
            "agents": {
                "test-agent": {
                    "model_provider": "test-provider",
                    "model": "test-model",
                    "prompt_version": "v1",
                    "cache": True,
                    "max_tokens": 1000,
                    "temperature": 0.5,
                    "tags": ["test"]
                }
            }
        },
        "database": database_config,
        "startup_tasks": {
            "DatabaseSchemaStartupTask": {
                "enabled": True
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="wb", delete=False) as temp:
        yaml.dump(test_config, temp, encoding="utf-8")
        temp_path = temp.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)

# In-memory SQLite database fixture
@pytest.fixture(scope="function")
async def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    db_context = DbContext("sqlite+aiosqlite:///:memory:")
    await db_context.initialize()
    
    # Create TestEntity table manually with SQL
    await db_context.execute(text("""
    CREATE TABLE test_entities (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        value INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        tenant_id VARCHAR
    )
    """))
    
    yield db_context
    
    # Clean up after test
    await db_context.close()

# Initialized engine fixture
@pytest.fixture(scope="function")
async def initialized_engine(test_config_file):
    """Initialize and start the engine with test configuration."""
    # Reset engine state
    Engine._instance = None
    
    # Set config file path
    os.environ["CONFIG_FILE"] = test_config_file
    
    # Get fresh engine
    test_engine = Engine.initialize()
    
    # Start engine asynchronously
    await test_engine.start()
    
    # Pre-register IEngine (should already be registered during start)
    test_engine.register(IEngine, test_engine)
    
    yield test_engine
    
    # Clean up any resources
    await test_engine.stop()
    test_engine._started = False
    Engine._instance = None
    if "CONFIG_FILE" in os.environ:
        del os.environ["CONFIG_FILE"]
