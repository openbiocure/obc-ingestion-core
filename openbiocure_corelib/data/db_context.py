"""Database context implementation for SQLAlchemy async operations."""

import logging
from typing import Any, Dict, Optional, Protocol, Union

from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import Executable

from openbiocure_corelib.config.app_config import DatabaseConfig

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

        # Immediate synchronous initialization
        self._initialize_sync()

    def _initialize_sync(self) -> None:
        """Initialize the database context synchronously."""
        try:
            # Create engine
            self._engine = create_async_engine(
                self.connection_string, echo=False, future=True
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine, expire_on_commit=False, class_=AsyncSession
            )

            # Create session
            if self._session_factory:
                self._session = self._session_factory()

            logger.debug(f"DbContext initialized with {self.connection_string}")
        except Exception as e:
            logger.error(f"Failed to initialize DbContext: {str(e)}")
            raise

    async def initialize(self) -> None:
        """Initialize the database context."""
        # This method now just ensures the context is initialized
        # but doesn't re-initialize if already done
        if self._session is None:
            self._initialize_sync()

    async def close(self) -> None:
        """Close the database context."""
        if self._session:
            await self._session.close()
            self._session = None

        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def execute(
        self, query: Executable, parameters: Optional[Dict[str, Any]] = None
    ) -> Result:
        """Execute a raw SQL query.

        Args:
            query: The query to execute
            parameters: Optional parameters for the query

        Returns:
            The result of the execution
        """
        if self._session is None:
            await self.initialize()

        if self._session is None:
            raise RuntimeError("Failed to initialize session")

        if parameters:
            result = await self._session.execute(query, parameters)
        else:
            result = await self._session.execute(query)

        await self._session.commit()
        return result

    @property
    def session(self) -> AsyncSession:
        """Get the current session."""
        if self._session is None:
            # If somehow the session is not initialized, initialize it
            self._initialize_sync()

        if self._session is None:
            raise RuntimeError("Failed to initialize session")

        return self._session

    async def create_schema(self):
        """Create database schema for all registered entities."""

        logger.info("Creating database schema...")

        # Make sure engine is initialized
        if self._engine is None:
            await self.initialize()

        # Get the metadata from BaseEntity
        from openbiocure_corelib.data.entity import BaseEntity

        # Create all tables
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(BaseEntity.metadata.create_all)

            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            raise
