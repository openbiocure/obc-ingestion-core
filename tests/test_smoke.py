"""Smoke tests for HerpAI-Lib."""
import pytest
from openbiocure_corelib import engine
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.core.startup_task import StartupTask
from openbiocure_corelib.core.startup_task_executor import StartupTaskExecutor
from openbiocure_corelib.data.entity import BaseEntity

def test_import_core_modules():
    """Test that core modules can be imported."""
    # Check engine
    assert engine is not None
    assert isinstance(engine, Engine)
    
    # Check that base classes are importable
    assert issubclass(StartupTask, object)
    assert issubclass(BaseEntity, object)
