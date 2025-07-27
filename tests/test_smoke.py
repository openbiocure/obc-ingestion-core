"""Smoke tests for HerpAI-Lib."""

from obc_ingestion_core import engine
from obc_ingestion_core.core.engine import Engine
from obc_ingestion_core.core.startup_task import StartupTask
from obc_ingestion_core.data.entity import BaseEntity


def test_import_core_modules():
    """Test that core modules can be imported."""
    # Check engine
    assert engine is not None
    assert isinstance(engine, Engine)

    # Check that base classes are importable
    assert issubclass(StartupTask, object)
    assert issubclass(BaseEntity, object)
