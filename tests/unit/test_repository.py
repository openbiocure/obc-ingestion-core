"""Tests for the Repository implementation."""
import pytest
from src.data.specification import Specification
from tests.mocks.mock_implementations import TestEntity, MockRepository

class TestEntityByNameSpecification(Specification[TestEntity]):
    """Specification to find TestEntity by name."""
    def __init__(self, name: str):
        self.name = name
    
    def is_satisfied_by(self, entity: TestEntity) -> bool:
        return entity.name == self.name
    
    def to_expression(self):
        return TestEntity.name == self.name

class TestEntityActiveSpecification(Specification[TestEntity]):
    """Specification to find active TestEntities."""
    def is_satisfied_by(self, entity: TestEntity) -> bool:
        return entity.is_active
    
    def to_expression(self):
        return TestEntity.is_active == True

@pytest.mark.asyncio
async def test_mock_repository_crud():
    """Test CRUD operations on MockRepository."""
    # Create repository
    repo = MockRepository(TestEntity)
    
    # Create entity
    entity = TestEntity(name="Test Entity", value=42)
    created = await repo.create(entity)
    
    # Check entity created
    assert created.id is not None
    assert created.name == "Test Entity"
    assert created.value == 42
    assert created.is_active == True
    
    # Read entity
    retrieved = await repo.get(created.id)
    assert retrieved is created
    
    # Update entity
    created.name = "Updated Name"
    created.value = 100
    updated = await repo.update(created)
    assert updated is created
    assert updated.name == "Updated Name"
    assert updated.value == 100
    
    # Delete entity
    deleted = await repo.delete(created.id)
    assert deleted is True
    
    # Check entity deleted
    not_found = await repo.get(created.id)
    assert not_found is None

@pytest.mark.asyncio
async def test_mock_repository_specifications():
    """Test using specifications with MockRepository."""
    # Create repository
    repo = MockRepository(TestEntity)
    
    # Create test entities
    entity1 = TestEntity(name="Entity 1", value=10, is_active=True)
    entity2 = TestEntity(name="Entity 2", value=20, is_active=True)
    entity3 = TestEntity(name="Entity 3", value=30, is_active=False)
    
    await repo.create(entity1)
    await repo.create(entity2)
    await repo.create(entity3)
    
    # Find by name
    by_name = await repo.find(TestEntityByNameSpecification("Entity 2"))
    assert len(by_name) == 1
    assert by_name[0] is entity2
    
    # Find active
    active = await repo.find(TestEntityActiveSpecification())
    assert len(active) == 2
    assert entity1 in active
    assert entity2 in active
    assert entity3 not in active
    
    # Find with combined specification
    combined = TestEntityActiveSpecification().and_(TestEntityByNameSpecification("Entity 1"))
    by_combined = await repo.find(combined)
    assert len(by_combined) == 1
    assert by_combined[0] is entity1
