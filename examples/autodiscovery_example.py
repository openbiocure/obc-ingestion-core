import asyncio
import logging
from src import engine
from src.config.yaml_config import YamlConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Initialize and start the engine 
    # It will auto-discover and execute startup tasks
    engine.initialize()
    engine.start()
    
    # Access configuration that was loaded by a startup task
    config = YamlConfig.get_instance()
    
    # Print some configuration values
    print("\nConfiguration Values:")
    print(f"Default Model Provider: {config.get('app.default_model_provider')}")
    
    # Print information about startup tasks
    print("\nStartup Tasks:")
    for task_name, task in engine._startup_task_executor._tasks.items():
        status = "Enabled" if task.enabled else "Disabled"
        print(f"- {task_name} (Order: {task.order}, Status: {status})")

if __name__ == "__main__":
    asyncio.run(main())
