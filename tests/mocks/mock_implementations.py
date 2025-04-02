"""Mock implementations for testing HerpAI-Lib."""
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic

from openbiocure_corelib.core.startup_task import StartupTask
from openbiocure_corelib.data.entity import BaseEntity
from openbiocure_corelib.data.specification import ISpecification
from sqlalchemy.orm import Mapped, mapped_column

T = TypeVar('T', bound=BaseEntity)

# Test entity for database operations
class TestEntity(BaseEntity):
    """Test entity for database tests."""
    __tablename__ = "test_entities"
    
    name: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    def __init__(self, **kwargs):
        # Ensure is_active has a default value
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
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
    
    async def create(self, entity: T) -> T:
        """Create an entity in the mock repository."""
        if not hasattr(entity, 'id') or getattr(entity, 'id') is None:
            setattr(entity, 'id', f"{self._next_id}")
            self._next_id += 1
        
        entity_id = getattr(entity, 'id')
        
        # Set generated values if not present
        if not hasattr(entity, 'created_at') or getattr(entity, 'created_at') is None:
            setattr(entity, 'created_at', datetime.now(UTC))
        
        if not hasattr(entity, 'updated_at') or getattr(entity, 'updated_at') is None:
            setattr(entity, 'updated_at', datetime.now(UTC))
        
        self._entities[entity_id] = entity
        return entity
    
    async def get(self, id: str) -> Optional[T]:
        """Get an entity by ID."""
        return self._entities.get(id)
    
    async def update(self, entity: T) -> Optional[T]:
        """Update an entity."""
        if not hasattr(entity, 'id'):
            return None
        
        entity_id = getattr(entity, 'id')
        if entity_id not in self._entities:
            return None
        
        # Update timestamps
        setattr(entity, 'updated_at', datetime.now(UTC))
        
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
            entity for entity in self._entities.values()
            if spec.is_satisfied_by(entity)
        ]
    
    async def find_one(self, spec: ISpecification[T]) -> Optional[T]:
        """Find the first entity matching the specification."""
        results = await self.find(spec)
        return results[0] if results else None
