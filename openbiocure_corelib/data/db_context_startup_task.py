"""Database context startup task."""
import logging
from openbiocure_corelib.core.startup_task import StartupTask
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.data.db_context import DbContext, IDbContext

logger = logging.getLogger(__name__)

class DatabaseSchemaStartupTask(StartupTask):
    """Startup task that creates the database schema."""
    
    order = 1
    
    async def execute(self) -> None:
        """Execute the startup task."""
        try:
            # Get database configuration
            config = Engine.current().config
            db_config = config.get("database", {})
            
            # Get connection string directly or build it from parameters
            if "connection_string" in db_config:
                connection_string = db_config["connection_string"]
            else:
                # Build connection string from individual parameters
                dialect = db_config.get("dialect", "sqlite")
                driver = db_config.get("driver", "aiosqlite")
                host = db_config.get("host", "localhost")
                port = db_config.get("port", "5432")
                database = db_config.get("database", "herpai")
                username = db_config.get("username", "")
                password = db_config.get("password", "")
                
                if dialect == "sqlite":
                    # For SQLite, create a file-based database in the db directory
                    connection_string = f"{dialect}+{driver}:///./db/{database}.db"
                else:
                    # For other databases, use full connection string
                    connection_string = f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"
            
            # Create database context
            db_context = DbContext(connection_string)
            
            # Register database context
            engine = Engine.current()
            engine.register(IDbContext, db_context)
            engine.register(DbContext, db_context)
            
            # Create schema
            await db_context.create_schema()
            
        except Exception as e:
            logger.error(f"Failed to create database schema: {str(e)}")
            raise