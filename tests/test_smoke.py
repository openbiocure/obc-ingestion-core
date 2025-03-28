"""Smoke tests for HerpAI-Lib."""
import pytest
from src import engine
from src.core.engine import Engine
from src.core.startup_task import StartupTask
from src.core.startup_task_executor import StartupTaskExecutor
from src.data.entity import BaseEntity

def test_import_core_modules():
    """Test that core modules can be imported."""
    # Check engine
    assert engine is not None
    assert isinstance(engine, Engine)
    
    # Check that base classes are importable
    assert issubclass(StartupTask, object)
    assert issubclass(BaseEntity, object)
