"""
YAML Configuration Example

This example demonstrates how to use the YAML configuration
system with dotted access.
"""
import asyncio
from openbiocure_corelib import engine
from openbiocure_corelib.config.yaml_config import YamlConfig

async def main():
    # Initialize and start the engine with auto-discovered tasks
    engine.initialize()
    await engine.start()
    
    # Get the configuration
    config = engine.resolve(YamlConfig)
    
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
