from typing import AsyncContextManager, Optional, Callable, Any, Protocol
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

class IDbContext(Protocol):
    @asynccontextmanager
    async def begin_transaction(self) -> AsyncContextManager[None]: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
    async def execute(self, statement: Any) -> Any: ...
    async def close(self) -> None: ...
    def get_session(self) -> AsyncSession: ...

class DbContext(IDbContext):
    def __init__(self, connection_string: str):
        self._engine = create_async_engine(connection_string)
        self._session_factory = async_sessionmaker(
            self._engine, expire_on_commit=False
        )
        self._session: Optional[AsyncSession] = None
    
    async def initialize(self) -> None:
        if self._session is None:
            self._session = self._session_factory()
    
    @asynccontextmanager
    async def begin_transaction(self) -> AsyncContextManager[None]:
        await self.initialize()
        async with self._session.begin():
            yield
    
    async def commit(self) -> None:
        if self._session:
            await self._session.commit()
    
    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()
    
    async def execute(self, statement: Any) -> Any:
        await self.initialize()
        return await self._session.execute(statement)
    
    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
    
    def get_session(self) -> AsyncSession:
        if self._session is None:
            raise ValueError("Session not initialized. Call initialize() first.")
        return self._session
