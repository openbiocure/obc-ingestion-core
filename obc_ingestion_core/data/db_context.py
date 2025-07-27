"""Database context implementation for SQLAlchemy async operations."""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Protocol, Union

from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import Executable

from obc_ingestion_core.config.app_config import DatabaseConfig

logger = logging.getLogger(__name__)


class IDbContext(Protocol):
    """Database context interface."""

    async def initialize(self) -> None:
        """Initialize the database context."""
        ...

    async def close(self) -> None:
        """Close the database context."""
        ...

    async def execute(
        self, query: Executable, parameters: Optional[Dict[str, Any]] = None
    ) -> Result:
        """Execute a raw SQL query."""
        ...

    @property
    def session(self) -> AsyncSession:
        """Get the current session."""
        ...

    @asynccontextmanager
    async def session_context(self):
        """Get a managed session context."""
        ...


class DbContext:
    """Database context implementation for SQLAlchemy async operations."""

    def __init__(self, connection_string_or_config: Union[str, DatabaseConfig]):
        """Initialize a new instance of the DbContext class."""
        if isinstance(connection_string_or_config, DatabaseConfig):
            self.connection_string = connection_string_or_config.connection_string
        else:
            self.connection_string = connection_string_or_config

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[Any] = None
        self._session: Optional[AsyncSession] = None
        self._is_initialized = False

    def _initialize_sync(self) -> None:
        """Initialize the database context synchronously."""
        if self._is_initialized:
            return
            
        try:
            # Create engine
            self._engine = create_async_engine(
                self.connection_string, 
                echo=False, 
                future=True,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine, 
                expire_on_commit=False, 
                class_=AsyncSession,
                autoflush=False,     # Disable autoflush for better control
            )

            self._is_initialized = True
            logger.debug(f"DbContext initialized with {self.connection_string}")
        except Exception as e:
            logger.error(f"Failed to initialize DbContext: {str(e)}")
            raise

    async def initialize(self) -> None:
        """Initialize the database context."""
        if not self._is_initialized:
            self._initialize_sync()

    async def close(self) -> None:
        """Close the database context."""
        try:
            if self._session:
                await self._session.close()
                self._session = None

            if self._engine:
                await self._engine.dispose()
                self._engine = None
                
            self._is_initialized = False
            logger.debug("DbContext closed successfully")
        except Exception as e:
            logger.error(f"Error closing DbContext: {str(e)}")
            raise

    @asynccontextmanager
    async def session_context(self):
        """Get a managed session context that ensures proper cleanup."""
        if not self._is_initialized:
            await self.initialize()
            
        session = None
        try:
            if self._session_factory:
                session = self._session_factory()
                yield session
            else:
                raise RuntimeError("Session factory not initialized")
        except Exception as e:
            if session:
                await session.rollback()
            logger.error(f"Error in session context: {str(e)}")
            raise
        finally:
            if session:
                await session.close()
                logger.debug("Session closed in context manager")

    async def execute(
        self, query: Executable, parameters: Optional[Dict[str, Any]] = None
    ) -> Result:
        """Execute a raw SQL query with proper session management.

        Args:
            query: The query to execute
            parameters: Optional parameters for the query

        Returns:
            The result of the execution
        """
        async with self.session_context() as session:
            try:
                if parameters:
                    result = await session.execute(query, parameters)
                else:
                    result = await session.execute(query)

                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Error executing query: {str(e)}")
                raise

    @property
    def session(self) -> AsyncSession:
        """Get the current session. Use session_context() for better lifecycle management."""
        if not self._is_initialized:
            self._initialize_sync()

        if self._session is None and self._session_factory:
            self._session = self._session_factory()

        if self._session is None:
            raise RuntimeError("Failed to initialize session")

        return self._session

    async def create_schema(self):
        """Create database schema for all registered entities."""

        logger.info("Creating database schema...")

        # Make sure engine is initialized
        if not self._is_initialized:
            await self.initialize()

        # Get the metadata from BaseEntity
        from obc_ingestion_core.data.entity import BaseEntity

        # Create all tables
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(BaseEntity.metadata.create_all)

            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            raise
