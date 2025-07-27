"""Mock implementations for testing HerpAI-Lib."""

from datetime import datetime, timezone
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column

from obc_ingestion_core.core.startup_task import StartupTask
from obc_ingestion_core.data.entity import BaseEntity
from obc_ingestion_core.data.specification import ISpecification

T = TypeVar("T", bound=BaseEntity)


# Test entity for database operations
class TestEntity(BaseEntity):
    """Test entity for database tests."""

    __tablename__ = "test_entities"

    name: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    def __init__(self, **kwargs: object):
        # Ensure is_active has a default value
        if "is_active" not in kwargs:
            kwargs["is_active"] = True
        # Validate required fields
        if "name" in kwargs and kwargs["name"] is None:
            raise SQLAlchemyError("name cannot be None")
        super().__init__(**kwargs)


# Mock startup task for testing
class MockStartupTask(StartupTask):
    """Mock startup task for testing."""

    order = 999
    executed = False

    async def execute(self) -> None:
        """Execute the mock task."""
        MockStartupTask.executed = True


# Mock repository for testing
class MockRepository(Generic[T]):
    """Mock repository for testing."""

    def __init__(self, entity_type: Type[T]):
        self._entity_type = entity_type
        self._entities: Dict[str, T] = {}
        self._next_id = 1

    async def create(self, entity: Optional[T] = None, **kwargs) -> T:
        """Create an entity in the mock repository."""
        # If an entity is provided, use it
        if entity is not None:
            if not isinstance(entity, self._entity_type):
                raise SQLAlchemyError("Invalid entity type")
            new_entity = entity
        else:
            # Create new entity from kwargs
            new_entity = self._entity_type(**kwargs)

        # Set ID if not present
        if not hasattr(new_entity, "id") or getattr(new_entity, "id") is None:
            setattr(new_entity, "id", f"{self._next_id}")
            self._next_id += 1

        entity_id = getattr(new_entity, "id")

        # Set generated values if not present
        if (
            not hasattr(new_entity, "created_at")
            or getattr(new_entity, "created_at") is None
        ):
            setattr(new_entity, "created_at", datetime.now(timezone.utc))

        if (
            not hasattr(new_entity, "updated_at")
            or getattr(new_entity, "updated_at") is None
        ):
            setattr(new_entity, "updated_at", datetime.now(timezone.utc))

        self._entities[entity_id] = new_entity
        return new_entity

    async def get(self, id: str) -> Optional[T]:
        """Get an entity by ID."""
        return self._entities.get(id)

    async def update(self, id_or_entity: Union[str, T], **kwargs) -> Optional[T]:
        """Update an entity."""
        # Handle both cases: when an entity object is passed or when an id is passed
        if isinstance(id_or_entity, str):
            entity_id = id_or_entity
            if entity_id not in self._entities:
                return None
            entity = self._entities[entity_id]
            # Update entity with kwargs, excluding immutable fields
            for key, value in kwargs.items():
                if key not in ["id", "created_at"] and not key.startswith("_"):
                    setattr(entity, key, value)
        else:
            # An entity object was passed
            entity = id_or_entity
            if not hasattr(entity, "id"):
                return None
            entity_id = getattr(entity, "id")
            if entity_id not in self._entities:
                return None

        # Update timestamps
        setattr(entity, "updated_at", datetime.now(timezone.utc))

        # Store updated entity
        self._entities[entity_id] = entity

        return entity

    async def delete(self, id: str) -> bool:
        """Delete an entity by ID."""
        if id in self._entities:
            del self._entities[id]
            return True
        return False

    async def find(self, spec: ISpecification[T]) -> List[T]:
        """Find entities matching the specification."""
        return [
            entity for entity in self._entities.values() if spec.is_satisfied_by(entity)
        ]

    async def find_one(self, spec: ISpecification[T]) -> Optional[T]:
        """Find the first entity matching the specification."""
        results = await self.find(spec)
        return results[0] if results else None
