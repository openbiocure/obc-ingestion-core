#!/bin/bash

echo "Fixing DbContext execute method to accept parameters..."

# Update the db_context.py file to fix the execute method
cat > src/data/db_context.py << 'EOF'
"""Database context implementation for SQLAlchemy async operations."""
from typing import Protocol, Optional, Any, Dict, Union
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.sql import Executable
from sqlalchemy.engine import Result

class IDbContext(Protocol):
    """Database context interface."""
    
    async def initialize(self) -> None:
        """Initialize the database context."""
        ...
    
    async def close(self) -> None:
        """Close the database context."""
        ...
    
    async def execute(self, query: Executable, parameters: Optional[Dict[str, Any]] = None) -> Result:
        """Execute a raw SQL query."""
        ...

class DbContext:
    """Database context implementation for SQLAlchemy async operations."""
    
    def __init__(self, connection_string: str):
        """Initialize a new instance of the DbContext class."""
        self.connection_string = connection_string
        self._engine: Optional[AsyncEngine] = None
        self._session_factory = None
        self._session: Optional[AsyncSession] = None
    
    async def initialize(self) -> None:
        """Initialize the database context."""
        self._engine = create_async_engine(
            self.connection_string,
            echo=False,
            future=True
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        self._session = self._session_factory()
    
    async def close(self) -> None:
        """Close the database context."""
        if self._session:
            await self._session.close()
        
        if self._engine:
            await self._engine.dispose()
    
    async def execute(self, query: Executable, parameters: Optional[Dict[str, Any]] = None) -> Result:
        """Execute a raw SQL query.
        
        Args:
            query: The query to execute
            parameters: Optional parameters for the query
            
        Returns:
            The result of the execution
        """
        if self._session is None:
            raise RuntimeError("Database context not initialized")
        
        if parameters:
            result = await self._session.execute(query, parameters)
        else:
            result = await self._session.execute(query)
        
        await self._session.commit()
        return result
EOF

echo "Fix completed. The DbContext.execute() method now accepts an optional parameters argument."