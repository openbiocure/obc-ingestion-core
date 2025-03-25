from typing import TypeVar, Generic, Type, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from herpailib.infrastructure.db.session import Database

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
        async with self.db.session() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.commit()  # <-- required
            await session.refresh(instance)
            return instance

    async def update(self, id: any, **kwargs) -> Optional[T]:
        async with self.db.session() as session:
            result = await session.get(self.model, id)
            if result:
                for key, value in kwargs.items():
                    setattr(result, key, value)
                await session.commit()  # <-- required
                await session.refresh(result)
            return result

    async def delete(self, id: any) -> bool:
        async with self.db.session() as session:
            result = await session.get(self.model, id)
            if result:
                await session.delete(result)
                await session.commit()  # <-- required
                return True
            return False
