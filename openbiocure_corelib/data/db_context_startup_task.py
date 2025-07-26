"""Database context startup task."""

import logging

from ..config.app_config import AppConfig
from ..core.engine import Engine
from ..core.startup_task import StartupTask
from .db_context import DbContext, IDbContext

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
            if db_config is None:
                logger.warning(
                    "No database configuration found, skipping database initialization"
                )
                return
            db_context = DbContext(db_config)

            # Register database context
            engine = Engine.current()
            engine.register(IDbContext, db_context)  # type: ignore
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
            db_context = engine.resolve(IDbContext)  # type: ignore

            # Close database context
            if db_context:
                await db_context.close()

            logger.info("Database context cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error cleaning up database context: {str(e)}")
