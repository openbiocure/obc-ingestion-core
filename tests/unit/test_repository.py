"""Tests for the Repository implementation."""
import pytest
from openbiocure_corelib.data.specification import Specification
from tests.mocks.mock_implementations import TestEntity, MockRepository
from sqlalchemy.exc import SQLAlchemyError

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

@pytest.mark.asyncio
async def test_repository_error_handling():
    """Test error handling in repository operations."""
    repo = MockRepository(TestEntity)
    
    # Test create with invalid data
    with pytest.raises(SQLAlchemyError):
        await repo.create(TestEntity(name=None))  # Assuming name is required
    
    # Test get with non-existent ID
    result = await repo.get("non-existent-id")
    assert result is None
    
    # Test update with non-existent ID
    result = await repo.update("non-existent-id", name="New Name")
    assert result is None
    
    # Test delete with non-existent ID
    result = await repo.delete("non-existent-id")
    assert result is False

@pytest.mark.asyncio
async def test_repository_update_edge_cases():
    """Test edge cases in repository update method."""
    repo = MockRepository(TestEntity)
    
    # Create initial entity
    entity = TestEntity(name="Test Entity", value=42)
    created = await repo.create(entity)
    
    # Test update with ID string
    updated = await repo.update(created.id, name="Updated by ID")
    assert updated.name == "Updated by ID"
    
    # Test update with empty kwargs
    updated = await repo.update(created)
    assert updated is created
    
    # Test update with None values
    updated = await repo.update(created.id, name=None)
    assert updated.name is None
    
    # Test update with immutable fields
    original_id = created.id
    original_created_at = created.created_at
    updated = await repo.update(created.id, id="new-id", created_at="2024-01-01")
    assert updated.id == original_id  # ID should not change
    assert updated.created_at == original_created_at  # created_at should not change

@pytest.mark.asyncio
async def test_repository_find_edge_cases():
    """Test edge cases in repository find method."""
    repo = MockRepository(TestEntity)
    
    # Test find with empty repository
    results = await repo.find(TestEntityActiveSpecification())
    assert len(results) == 0
    
    # Test find with no matching entities
    entity = TestEntity(name="Test Entity", value=42, is_active=False)
    await repo.create(entity)
    results = await repo.find(TestEntityActiveSpecification())
    assert len(results) == 0
    
    # Test find with complex specification
    spec = TestEntityActiveSpecification().and_(
        TestEntityByNameSpecification("Test Entity")
    ).or_(
        TestEntityByNameSpecification("Another Entity")
    )
    results = await repo.find(spec)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_repository_initialization():
    """Test repository initialization and configuration."""
    # Test repository initialization
    repo = MockRepository(TestEntity)
    assert repo._entity_type == TestEntity
    
    # Test repository with custom entity type
    class CustomEntity(TestEntity):
        pass
    
    custom_repo = MockRepository(CustomEntity)
    assert custom_repo._entity_type == CustomEntity
    
    # Test repository operations with custom entity
    entity = CustomEntity(name="Custom Entity", value=42)
    created = await custom_repo.create(entity)
    assert isinstance(created, CustomEntity)
    assert created.name == "Custom Entity"
