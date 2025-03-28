"""
YAML Configuration Example

This example demonstrates how to use the YAML configuration
system with dotted access.
"""
import asyncio
from src import engine
from src.config.yaml_config import YamlConfig
from src.core.startup import ConfigurationStartupTask

async def main():
    # Add configuration startup task
    # Note: In production, this would be auto-discovered
    config_task = ConfigurationStartupTask()
    config_task.configure({'path': 'config.yaml'})
    engine.add_startup_task(config_task)
    
    # Initialize and start the engine
    engine.initialize()
    engine.start()
    
    # Get the configuration
    config = YamlConfig.get_instance()
    
    # Access configuration using dot notation
    print("YAML Configuration Example:")
    print("===========================")
    
    print("\nDatabase Configuration:")
    print(f"Host: {config.get('database.host')}")
    print(f"Port: {config.get('database.port')}")
    print(f"Database: {config.get('database.database')}")
    
    print("\nDefault Model Provider:")
    print(f"{config.get('app.default_model_provider')}")
    
    print("\nAgent Configurations:")
    for agent_name in config.get('app.agents', {}).keys():
        print(f"\n{agent_name}:")
        agent_config = config.get(f'app.agents.{agent_name}')
        print(f"  Model: {agent_config.get('model')}")
        print(f"  Temperature: {agent_config.get('temperature')}")
        print(f"  Tags: {', '.join(agent_config.get('tags', []))}")

if __name__ == "__main__":
    asyncio.run(main())
