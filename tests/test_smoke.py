"""Smoke tests for HerpAI-Lib."""
import pytest
from src import engine
from src.core.engine import Engine
from src.core.startup import StartupTask, StartupTaskExecutor
from src.data.entity import BaseEntity
from src.data.repository import Repository, IRepository
from src.config.yaml_config import YamlConfig
from src.config.dataclass_config import AppConfig

def test_import_core_modules():
    """Test that core modules can be imported."""
    # Check engine
    assert engine is not None
    assert isinstance(engine, Engine)
    
    # Check that base classes are importable
    assert issubclass(StartupTask, object)
    assert issubclass(BaseEntity, object)

@pytest.mark.asyncio
async def test_basic_functionality(test_config_file):
    """Simple smoke test of basic functionality."""
    # Initialize engine
    test_engine = Engine()
    
    # Add config task
    config_task = StartupTask()
    config_task.execute = lambda: YamlConfig.get_instance().load(test_config_file)
    
    task_executor = StartupTaskExecutor()
    task_executor.add_task(config_task)
    test_engine._startup_task_executor = task_executor
    
    # Start engine
    test_engine._started = False
    test_engine.start()
    
    # Check engine started
    assert test_engine._started
    
    # Register a simple service
    class SimpleService:
        def get_value(self):
            return "test_value"
    
    service = SimpleService()
    test_engine.register(SimpleService, service)
    
    # Resolve service
    resolved = test_engine.resolve(SimpleService)
    assert resolved is service
    assert resolved.get_value() == "test_value"
