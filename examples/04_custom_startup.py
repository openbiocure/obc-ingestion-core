"""
Custom Startup Task Example

This example demonstrates how to create and use custom startup tasks
with auto-discovery, ordering, and configuration.
"""

import asyncio
import logging
from obc_ingestion_core import engine
from obc_ingestion_core.core.startup_task import StartupTask

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Define a custom startup task
class DatabaseInitializationTask(StartupTask):
    """Custom startup task to initialize the database."""

    # Run after configuration is loaded (order 10-20)
    order = 30

    async def execute(self) -> None:
        """Execute the database initialization."""
        logger.info("Initializing database...")

        # Get configuration parameters from task config
        schema_name = self._config.get("schema", "public")
        create_tables = self._config.get("create_tables", True)

        logger.info(f"Using schema: {schema_name}")
        logger.info(f"Create tables: {create_tables}")

        # In a real app, you'd create database tables here
        # ...


# Define another custom startup task
class ModelInitializationTask(StartupTask):
    """Custom startup task to initialize AI models."""

    # Run after database initialization
    order = 40

    async def execute(self) -> None:
        """Execute the model initialization."""
        logger.info("Initializing AI models...")

        # Get configuration parameters
        default_model = self._config.get("default_model", "default")
        preload = self._config.get("preload", False)

        logger.info(f"Default model: {default_model}")
        logger.info(f"Preload models: {preload}")

        # In a real app, you'd initialize models here
        # ...


async def main():
    # Initialize and start the engine
    # The engine will auto-discover our tasks
    engine.initialize()
    await engine.start()

    # Print information about discovered tasks
    print("\nStartup Tasks:")
    for task_name, task in engine._startup_task_executor._tasks.items():
        status = "Enabled" if task.enabled else "Disabled"
        print(f"- {task_name} (Order: {task.order}, Status: {status})")

    # Print startup task configuration
    from obc_ingestion_core.config.yaml_config import YamlConfig

    config = engine.resolve(YamlConfig)

    print("\nStartup Task Configuration:")
    startup_tasks_config = config.get("startup_tasks", {})
    for task_name, task_config in startup_tasks_config.items():
        print(f"\n{task_name}:")
        for key, value in task_config.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
