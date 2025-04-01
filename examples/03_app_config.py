"""
AppConfig Example

This example demonstrates how to use the strongly-typed
AppConfig with dataclasses for configuration.
"""
import asyncio
from openbiocure_corelib import engine
from openbiocure_corelib.config.dataclass_config import AppConfig

async def main():
    # Initialize and start the engine with auto-discovered tasks
    engine.initialize()
    await engine.start()
    
    # Get the typed configuration
    app_config = AppConfig.get_instance()
    
    print("AppConfig Example:")
    print("=================")
    
    print(f"\nDefault Model Provider: {app_config.default_model_provider}")
    
    print("\nDatabase Configuration:")
    if app_config.db_config:
        print(f"Connection String: {app_config.db_config.connection_string}")
        print(f"Dialect: {app_config.db_config.dialect}")
        print(f"Driver: {app_config.db_config.driver}")
    else:
        print("No database configuration found")
    
    print("\nAgent Configurations:")
    for name, agent in app_config.agents.items():
        print(f"\n{name}:")
        print(f"  Model Provider: {agent.model_provider}")
        print(f"  Model: {agent.model}")
        print(f"  Temperature: {agent.temperature}")
        print(f"  Max Tokens: {agent.max_tokens}")
        print(f"  Cache Enabled: {'Yes' if agent.cache else 'No'}")
        print(f"  Tags: {', '.join(agent.tags) if agent.tags else 'None'}")
        print(f"  Research Domain: {'Yes' if agent.is_research_domain else 'No'}")
    
    # Get a database session
    try:
        session = app_config.get_db_session()
        print(f"\nSuccessfully connected to database: {app_config.db_config.database}")
    except Exception as e:
        print(f"\nCouldn't connect to database: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
