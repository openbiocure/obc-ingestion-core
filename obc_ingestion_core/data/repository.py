import logging
import uuid
from abc import abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Generic, List, Optional, Protocol, Type, TypeVar, Union

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .entity import BaseEntity
from .specification import ISpecification

# Create a logger for the repository module
logger = logging.getLogger(__name__)

# Type variable for entity types
T = TypeVar("T", bound=BaseEntity)


class IRepository(Generic[T], Protocol):
    """
    Generic repository interface that defines standard operations for entity persistence.

    This interface provides a contract for implementing repositories that handle
    CRUD operations for entity types that inherit from BaseEntity.

    Type Parameters:
        T: The entity type, must be a subclass of BaseEntity
    """

    @abstractmethod
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

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Get an entity by its ID"""
        ...

    @abstractmethod
    async def update(self, id_or_entity: Union[str, T], **kwargs) -> Optional[T]:
        """Update an entity by its ID or using an entity object"""
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an entity by its ID"""
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

    async def find_one(self, spec: ISpecification[T]) -> Optional[T]:
        """
        Find the first entity that matches the given specification.

        Args:
            spec: The specification to match against

        Returns:
            The first matching entity if found, None otherwise
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
                k: v for k, v in entity.__dict__.items() if not k.startswith("_")
            }
            kwargs.update(entity_dict)
        else:
            logger.debug(f"Creating {self._entity_type.__name__} from kwargs")

        # Generate ID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
            logger.debug(f"Generated new ID: {kwargs['id']}")

        try:
            stmt = (
                insert(self._entity_type).values(**kwargs).returning(self._entity_type)
            )
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
            logger.error(
                f"Error getting {self._entity_type.__name__} with ID {id}: {str(e)}"
            )
            raise

    async def update(self, id_or_entity: Union[str, T], **kwargs) -> Optional[T]:
        """
        Update an entity by its ID.

        Args:
            id_or_entity: Either the unique identifier of the entity or the entity object itself
            **kwargs: The attributes to update (if id is provided)

        Returns:
            The updated entity if found, None otherwise
        """
        # Handle both cases: when an entity object is passed or when an id is passed
        if isinstance(id_or_entity, str):
            entity_id = id_or_entity
            update_values = kwargs
        else:
            # An entity object was passed
            entity = id_or_entity
            entity_id = entity.id
            # Convert entity to a dictionary of values, excluding None values
            update_values = {
                k: v
                for k, v in entity.__dict__.items()
                if not k.startswith("_") and v is not None
            }

        logger.debug(f"Updating {self._entity_type.__name__} with ID: {entity_id}")

        # Remove immutable fields
        update_values.pop("id", None)
        update_values.pop("created_at", None)

        # Set updated_at
        update_values["updated_at"] = datetime.now(timezone.utc)

        try:
            stmt = (
                update(self._entity_type)
                .where(self._entity_type.id == entity_id)
                .values(**update_values)
                .returning(self._entity_type)
            )
            result = await self._session.execute(stmt)
            await self._session.commit()
            updated_entity = result.scalar_one_or_none()
            if updated_entity:
                logger.info(
                    f"Updated {self._entity_type.__name__} with ID: {entity_id}"
                )
            else:
                logger.warning(
                    f"No {self._entity_type.__name__} found with ID: {entity_id} for update"
                )
            return updated_entity
        except Exception as e:
            await self._session.rollback()
            logger.error(
                f"Error updating {self._entity_type.__name__} with ID {entity_id}: {str(e)}"
            )
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
                logger.warning(
                    f"No {self._entity_type.__name__} found with ID: {id} for deletion"
                )
            return success
        except Exception as e:
            await self._session.rollback()
            logger.error(
                f"Error deleting {self._entity_type.__name__} with ID {id}: {str(e)}"
            )
            raise

    async def find(self, spec: ISpecification[T]) -> List[T]:
        """
        Find entities that match the given specification.

        Args:
            spec: The specification to match against

        Returns:
            A list of matching entities
        """
        logger.debug(
            f"Finding {self._entity_type.__name__} entities matching specification"
        )
        try:
            stmt = select(self._entity_type).where(spec.to_expression())
            result = await self._session.execute(stmt)
            entities = list(result.scalars().all())
            logger.debug(f"Found {len(entities)} {self._entity_type.__name__} entities")
            return entities
        except Exception as e:
            logger.error(
                f"Error finding {self._entity_type.__name__} entities: {str(e)}"
            )
            raise

    async def find_one(self, spec: ISpecification[T]) -> Optional[T]:
        """
        Find the first entity that matches the given specification.

        Args:
            spec: The specification to match against

        Returns:
            The first matching entity if found, None otherwise
        """
        logger.debug(
            f"Finding first {self._entity_type.__name__} entity matching specification"
        )
        try:
            stmt = select(self._entity_type).where(spec.to_expression()).limit(1)
            result = await self._session.execute(stmt)
            entity = result.scalar_one_or_none()
            if entity:
                logger.debug(
                    f"Found {self._entity_type.__name__} entity with ID: {entity.id}"
                )
            else:
                logger.debug(
                    f"No {self._entity_type.__name__} entity found matching specification"
                )
            return entity
        except Exception as e:
            logger.error(f"Error finding {self._entity_type.__name__} entity: {str(e)}")
            raise
