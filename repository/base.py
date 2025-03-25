from typing import TypeVar, Generic, Type, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.session import Database

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db: Database, model: Type[T]):
        self.db = db
        self.model = model

    async def get(self, id: any) -> Optional[T]:
        async with self.db.session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == id)
            )
            return result.scalar_one_or_none()

    async def create(self, **kwargs) -> T:
        async with self.db.transaction() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.flush()
            return instance

    async def update(self, id: any, **kwargs) -> Optional[T]:
        async with self.db.transaction() as session:
            instance = await self.get(id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.flush()
            return instance

    async def delete(self, id: any) -> bool:
        async with self.db.transaction() as session:
            instance = await self.get(id)
            if instance:
                await session.delete(instance)
                return True
            return False
