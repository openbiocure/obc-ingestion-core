from typing import TypeVar, Generic, Protocol, List, Optional, Type, Dict, Any
import uuid
import logging
from datetime import datetime, UTC
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from .specification import ISpecification
from .entity import BaseEntity

# Create a logger for the repository module
logger = logging.getLogger(__name__)

# Type variable for entity types
T = TypeVar('T', bound=BaseEntity)

class IRepository(Generic[T], Protocol):
    """
    Generic repository interface that defines standard operations for entity persistence.
    
    This interface provides a contract for implementing repositories that handle
    CRUD operations for entity types that inherit from BaseEntity.
    
    Type Parameters:
        T: The entity type, must be a subclass of BaseEntity
    """
    async def create(self, entity=None, **kwargs) -> T:
        """
        Create a new entity instance.
        
        Args:
            entity: The entity object to create (optional)
            **kwargs: The entity attributes as keyword arguments
            
        Returns:
            The created entity
        """
        ...
        
    async def get(self, id: str) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        ...
        
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            **kwargs: The attributes to update
            
        Returns:
            The updated entity if found, None otherwise
        """
        ...
        
    async def delete(self, id: str) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            True if the entity was deleted, False otherwise
        """
        ...
        
    async def find(self, spec: ISpecification[T]) -> List[T]:
        """
        Find entities that match the given specification.
        
        Args:
            spec: The specification to match against
            
        Returns:
            A list of matching entities
        """
        ...

class Repository(Generic[T], IRepository[T]):
    """
    Generic repository implementation that provides CRUD operations for entities.
    
    This class implements the IRepository interface and provides a concrete
    implementation of CRUD operations using SQLAlchemy for database access.
    
    Type Parameters:
        T: The entity type, must be a subclass of BaseEntity
    """
    
    def __init__(self, session: AsyncSession, entity_type: Type[T]):
        """
        Initialize a new repository instance.
        
        Args:
            session: The SQLAlchemy async session
            entity_type: The entity class
        """
        self._session = session
        self._entity_type = entity_type
        logger.debug(f"Initialized repository for entity type: {entity_type.__name__}")
    
    async def create(self, entity=None, **kwargs) -> T:
        """
        Create a new entity.
        
        Args:
            entity: The entity object to create (optional)
            **kwargs: The entity attributes
            
        Returns:
            The created entity
        """
        # If an entity is provided, extract its attributes
        if entity is not None:
            logger.debug(f"Creating {self._entity_type.__name__} from entity object")
            # Extract entity attributes, excluding SQLAlchemy-specific attributes
            entity_dict = {
                k: v for k, v in entity.__dict__.items() 
                if not k.startswith('_')
            }
            kwargs.update(entity_dict)
        else:
            logger.debug(f"Creating {self._entity_type.__name__} from kwargs")
        
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
            logger.debug(f"Generated new ID: {kwargs['id']}")
        
        try:
            stmt = insert(self._entity_type).values(**kwargs).returning(self._entity_type)
            result = await self._session.execute(stmt)
            await self._session.commit()
            entity = result.scalar_one()
            logger.info(f"Created {self._entity_type.__name__} with ID: {entity.id}")
            return entity
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error creating {self._entity_type.__name__}: {str(e)}")
            raise
    
    async def get(self, id: str) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        logger.debug(f"Getting {self._entity_type.__name__} with ID: {id}")
        try:
            stmt = select(self._entity_type).where(self._entity_type.id == id)
            result = await self._session.execute(stmt)
            entity = result.scalar_one_or_none()
            if entity:
                logger.debug(f"Found {self._entity_type.__name__} with ID: {id}")
            else:
                logger.debug(f"No {self._entity_type.__name__} found with ID: {id}")
            return entity
        except Exception as e:
            logger.error(f"Error getting {self._entity_type.__name__} with ID {id}: {str(e)}")
            raise
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            **kwargs: The attributes to update
            
        Returns:
            The updated entity if found, None otherwise
        """
        logger.debug(f"Updating {self._entity_type.__name__} with ID: {id}")
        
        # Remove immutable fields
        kwargs.pop('id', None)
        kwargs.pop('created_at', None)
        
        # Set updated_at
        kwargs['updated_at'] = datetime.now(UTC)
        
        try:
            stmt = (
                update(self._entity_type)
                .where(self._entity_type.id == id)
                .values(**kwargs)
                .returning(self._entity_type)
            )
            result = await self._session.execute(stmt)
            await self._session.commit()
            entity = result.scalar_one_or_none()
            if entity:
                logger.info(f"Updated {self._entity_type.__name__} with ID: {id}")
            else:
                logger.warning(f"No {self._entity_type.__name__} found with ID: {id} for update")
            return entity
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error updating {self._entity_type.__name__} with ID {id}: {str(e)}")
            raise
    
    async def delete(self, id: str) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            True if the entity was deleted, False otherwise
        """
        logger.debug(f"Deleting {self._entity_type.__name__} with ID: {id}")
        try:
            stmt = delete(self._entity_type).where(self._entity_type.id == id)
            result = await self._session.execute(stmt)
            await self._session.commit()
            success = result.rowcount > 0
            if success:
                logger.info(f"Deleted {self._entity_type.__name__} with ID: {id}")
            else:
                logger.warning(f"No {self._entity_type.__name__} found with ID: {id} for deletion")
            return success
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error deleting {self._entity_type.__name__} with ID {id}: {str(e)}")
            raise
    
    async def find(self, spec: ISpecification[T]) -> List[T]:
        """
        Find entities that match the given specification.
        
        Args:
            spec: The specification to match against
            
        Returns:
            A list of matching entities
        """
        logger.debug(f"Finding {self._entity_type.__name__} entities matching specification")
        try:
            stmt = select(self._entity_type).where(spec.to_expression())
            result = await self._session.execute(stmt)
            entities = result.scalars().all()
            logger.debug(f"Found {len(entities)} {self._entity_type.__name__} entities")
            return entities
        except Exception as e:
            logger.error(f"Error finding {self._entity_type.__name__} entities: {str(e)}")
            raise