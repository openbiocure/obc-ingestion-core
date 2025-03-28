from typing import TypeVar, Generic, Protocol, List, Optional, Type, Dict, Any
import uuid
from datetime import datetime, UTC
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from .specification import ISpecification
from .entity import BaseEntity

T = TypeVar('T', bound=BaseEntity)

class IRepository(Generic[T], Protocol):
    async def create(self, **kwargs) -> T: ...
    async def get(self, id: str) -> Optional[T]: ...
    async def update(self, id: str, **kwargs) -> Optional[T]: ...
    async def delete(self, id: str) -> bool: ...
    async def find(self, spec: ISpecification[T]) -> List[T]: ...

class Repository(Generic[T], IRepository[T]):
    def __init__(self, session: AsyncSession, entity_type: Type[T]):
        self._session = session
        self._entity_type = entity_type
    
    async def create(self, **kwargs) -> T:
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        stmt = insert(self._entity_type).values(**kwargs).returning(self._entity_type)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one()
    
    async def get(self, id: str) -> Optional[T]:
        stmt = select(self._entity_type).where(self._entity_type.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        # Remove immutable fields
        kwargs.pop('id', None)
        kwargs.pop('created_at', None)
        
        # Set updated_at
        kwargs['updated_at'] = datetime.now(UTC)
        
        stmt = (
            update(self._entity_type)
            .where(self._entity_type.id == id)
            .values(**kwargs)
            .returning(self._entity_type)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: str) -> bool:
        stmt = delete(self._entity_type).where(self._entity_type.id == id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0
    
    async def find(self, spec: ISpecification[T]) -> List[T]:
        stmt = select(self._entity_type).where(spec.to_expression())
        result = await self._session.execute(stmt)
        return result.scalars().all()
