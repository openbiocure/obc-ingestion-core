"""Database context startup task."""
import logging
from openbiocure_corelib.core.startup_task import StartupTask
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.data.db_context import DbContext, IDbContext
from openbiocure_corelib.config.app_config import AppConfig

logger = logging.getLogger(__name__)

class DatabaseSchemaStartupTask(StartupTask):
    """Startup task that creates the database schema."""
    
    order = 1
    
    async def execute(self) -> None:
        """Execute the startup task."""
        try:
            # Get database configuration from AppConfig
            app_config = AppConfig.get_instance()
            db_config = app_config.db_config
            
            # Create database context
            db_context = DbContext(db_config)
            
            # Register database context
            engine = Engine.current()
            engine.register(IDbContext, db_context)
            engine.register(DbContext, db_context)
            
            # Create schema
            await db_context.create_schema()
            
        except Exception as e:
            logger.error(f"Failed to create database schema: {str(e)}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up resources used by the startup task."""
        try:
            # Get database context
            engine = Engine.current()
            db_context = engine.resolve(IDbContext)
            
            # Close database context
            if db_context:
                await db_context.close()
                
            logger.info("Database context cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error cleaning up database context: {str(e)}")