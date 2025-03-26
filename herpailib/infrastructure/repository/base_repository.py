# herpailib/infrastructure/repository/base_repository.py

from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.base_entity import BaseEntity
from .interfaces import IRepository

T = TypeVar('T', bound=BaseEntity)

class BaseRepository(Generic[T], IRepository[T]):
    """
    Base repository implementation for CRUD operations.
    
    Generic type T must be a subclass of BaseEntity.
    Implements the IRepository interface.
    """
    
    def __init__(self, db: AsyncSession, entity: Type[T]):
        """
        Initialize the repository.
        
        Args:
            db: AsyncSession - The database session
            entity: Type[T] - The entity class to operate on
        """
        self.db = db
        self.entity = entity

    async def create(self, **kwargs) -> T:
        """
        Create a new entity instance.
        
        Args:
            **kwargs: The attributes to set on the new entity
            
        Returns:
            T: The created entity instance
        """
        instance = self.entity(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def get(self, id: str) -> Optional[T]:
        """
        Get an entity by ID.
        
        Args:
            id: str - The ID of the entity to retrieve
            
        Returns:
            Optional[T]: The found entity or None if not found
        """
        return await self.db.get(self.entity, id)

    async def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update an entity by ID.
        
        Args:
            id: str - The ID of the entity to update
            **kwargs: The attributes to update
            
        Returns:
            Optional[T]: The updated entity or None if not found
        """
        instance = await self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.db.flush()
            await self.db.refresh(instance)
        return instance

    async def delete(self, id: str) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            id: str - The ID of the entity to delete
            
        Returns:
            bool: True if entity was deleted, False if not found
        """
        instance = await self.get(id)
        if instance:
            await self.db.delete(instance)
            await self.db.flush()
            return True
        return False