# .herpai/core/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from herpailib.configuration.app_config import DatabaseConfig

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_async_engine(
            config.url,
            echo=config.echo,
            pool_pre_ping=True,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    async def initialize(self) -> None:
        """Initialize database by creating all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """Dispose of the database engine"""
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide an async session context manager"""
        session: AsyncSession = self.async_session_maker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional context manager"""
        async with self.session() as session:
            async with session.begin():
                try:
                    yield session
                except Exception as e:
                    await session.rollback()
                    raise e

# Usage example:
# .herpai/core/repository/base.py

# # Application startup
# # .herpai/main.py
# async def startup():
#     config = AppConfig.load("config.yaml")
#     db = Database(config.agents["ingestion"].database)
#     await db.initialize()
#     return db

# async def shutdown(db: Database):
#     await db.dispose()