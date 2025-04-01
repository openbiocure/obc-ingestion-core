"""Tests for the Startup Task system."""
import pytest
from openbiocure_corelib.core.startup_task import StartupTask
from openbiocure_corelib.core.startup_task_executor import StartupTaskExecutor
from tests.mocks.mock_implementations import MockStartupTask

def test_startup_task_ordering():
    """Test that startup tasks are executed in the correct order."""
    # Create tasks with different orders
    class Task1(StartupTask):
        order = 10
        executed = False
        def execute(self):
            Task1.executed = True
            assert not Task2.executed  # Task1 should execute before Task2
    
    class Task2(StartupTask):
        order = 20
        executed = False
        def execute(self):
            Task2.executed = True
            assert Task1.executed  # Task1 should have executed already
    
    # Reset execution state
    Task1.executed = False
    Task2.executed = False
    
    # Create executor and add tasks
    executor = StartupTaskExecutor()
    executor.add_task(Task2())  # Add in reverse order
    executor.add_task(Task1())
    
    # Execute tasks
    executor.execute_all()
    
    # Verify both executed
    assert Task1.executed
    assert Task2.executed

def test_startup_task_enabled():
    """Test that disabled startup tasks are not executed."""
    # Create enabled and disabled tasks
    class EnabledTask(StartupTask):
        order = 10
        enabled = True
        executed = False
        def execute(self):
            EnabledTask.executed = True
    
    class DisabledTask(StartupTask):
        order = 20
        enabled = False
        executed = False
        def execute(self):
            DisabledTask.executed = True
    
    # Reset execution state
    EnabledTask.executed = False
    DisabledTask.executed = False
    
    # Create executor and add tasks
    executor = StartupTaskExecutor()
    executor.add_task(EnabledTask())
    executor.add_task(DisabledTask())
    
    # Execute tasks
    executor.execute_all()
    
    # Verify only enabled task executed
    assert EnabledTask.executed
    assert not DisabledTask.executed

def test_startup_task_configuration():
    """Test that startup tasks can be configured."""
    # Create configurable task
    class ConfigurableTask(StartupTask):
        executed_with = None
        
        def execute(self):
            ConfigurableTask.executed_with = self._config.get('test_value')
    
    # Reset execution state
    ConfigurableTask.executed_with = None
    
    # Create executor and add task
    executor = StartupTaskExecutor()
    task = ConfigurableTask()
    executor.add_task(task)
    
    # Configure directly
    task._config = {'test_value': 'configured_value'}
    
    # Execute task
    executor.execute_all()
    
    # Verify configuration was used
    assert ConfigurableTask.executed_with == 'configured_value'
