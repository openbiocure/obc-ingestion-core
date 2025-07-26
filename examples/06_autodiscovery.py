"""
Auto-discovery Example

This example demonstrates how the engine auto-discovers
startup tasks and other components.
"""

import asyncio
import logging
from openbiocure_corelib import engine
from openbiocure_corelib.core.startup_task import StartupTask

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Define a new startup task that will be auto-discovered
class ExampleAutoDiscoveredTask(StartupTask):
    """Example task that will be auto-discovered."""

    order = 100  # Run late in the sequence
    enabled = True

    async def execute(self) -> None:
        """Execute the task."""
        logger.info("Auto-discovered task executed!")
        logger.info(f"Task configuration: {self._config}")


async def main():
    # Let the engine initialize without manually registering any tasks
    engine.initialize()
    await engine.start()

    print("\nAuto-discovered Startup Tasks:")
    for task_name, task in engine._startup_task_executor._tasks.items():
        status = "Enabled" if task.enabled else "Disabled"
        print(f"- {task_name} (Order: {task.order}, Status: {status})")

    print("\nLoaded Configuration:")
    try:
        from openbiocure_corelib.config.yaml_config import YamlConfig

        config = engine.resolve(YamlConfig)
        print(f"App Default Model Provider: {config.get('app.default_model_provider')}")
        print(f"Database Host: {config.get('database.host')}")

        # Print number of agents
        agents = config.get("app.agents", {})
        print(f"Number of configured agents: {len(agents)}")
    except Exception as e:
        print(f"Configuration not loaded: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
