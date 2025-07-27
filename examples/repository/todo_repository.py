from typing import List, Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from examples.domain.todo_entity import Todo
from obc_ingestion_core.data.repository import IRepository, Repository
from obc_ingestion_core.data.specification import Specification

# Define a Todo repository interface
class ITodoRepository(IRepository[Todo], Protocol):
    async def find_completed(self) -> List[Todo]: ...
    async def find_by_title(self, title: str) -> List[Todo]: ...

# Define specifications
class CompletedTodoSpecification(Specification[Todo]):
    def to_expression(self):
        return Todo.completed == True

class TitleContainsSpecification(Specification[Todo]):
    def __init__(self, text: str):
        self.text = text
    
    def to_expression(self):
        return Todo.title.contains(self.text)

# Implement the repository
class TodoRepository(Repository[Todo]):
    def __init__(self, session: AsyncSession, entity_type: type):
        super().__init__(session, entity_type)
    
    async def find_completed(self) -> List[Todo]:
        return await self.find(CompletedTodoSpecification())
    
    async def find_by_title(self, title: str) -> List[Todo]:
        return await self.find(TitleContainsSpecification(title))