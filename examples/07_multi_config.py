"""
Multi-configuration Example

This example demonstrates how to work with multiple
configuration sources - YAML and environment variables.
"""
import asyncio
import os
from openbiocure_corelib import engine
from openbiocure_corelib.core.startup import StartupTask
from openbiocure_corelib.config.yaml_config import YamlConfig
from openbiocure_corelib.config.environment import Environment

# Define a startup task to load environment variables
class EnvironmentStartupTask(StartupTask):
    """Startup task to load environment variables."""
    
    # Run before configuration
    order = 5
    
    async def execute(self) -> None:
        # Set some environment variables for demonstration
        os.environ["HERPAI_DB_HOST"] = "env-db-host"
        os.environ["HERPAI_DB_PORT"] = "5433"
        os.environ["HERPAI_API_KEY"] = "env-api-key-123"
        os.environ["HERPAI_DEBUG"] = "true"

async def main():
    # Initialize and start the engine
    engine.initialize()
    await engine.start()
    
    # Access YAML configuration
    yaml_config = engine.resolve(YamlConfig)
    
    print("Multi-configuration Example:")
    print("===========================")
    
    print("\nYAML Configuration:")
    print(f"Database Host (YAML): {yaml_config.get('database.host')}")
    print(f"Database Port (YAML): {yaml_config.get('database.port')}")
    
    print("\nEnvironment Variables:")
    print(f"Database Host (ENV): {Environment.get('HERPAI_DB_HOST')}")
    print(f"Database Port (ENV): {Environment.get('HERPAI_DB_PORT')}")
    print(f"API Key (ENV): {Environment.get('HERPAI_API_KEY')}")
    print(f"Debug Mode (ENV): {Environment.get_bool('HERPAI_DEBUG')}")
    
    print("\nMerged Configuration (Environment takes precedence):")
    db_host = Environment.get('HERPAI_DB_HOST') or yaml_config.get('database.host')
    db_port = Environment.get_int('HERPAI_DB_PORT') or yaml_config.get('database.port')
    print(f"Database Host (Merged): {db_host}")
    print(f"Database Port (Merged): {db_port}")

if __name__ == "__main__":
    asyncio.run(main())
