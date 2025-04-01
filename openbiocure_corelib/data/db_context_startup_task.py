import logging
import asyncio
from ..core.startup_task import StartupTask

logger = logging.getLogger(__name__)


class DatabaseSchemaStartupTask(StartupTask):
    """Startup task that creates the database schema."""
    
    # Run early in the startup process, after configuration
    order = 50
    
    async def execute(self):
        """Execute the task to create database schema asynchronously."""
        # Get the DbContext from the engine
        from .db_context import IDbContext
        from ..core.engine import Engine
        
        try:
            # Use the current engine instance
            engine = Engine.current()
            db_context = engine.resolve(IDbContext)
            await db_context.create_schema()
      
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Failed to create database schema: {str(e)}")
            raise