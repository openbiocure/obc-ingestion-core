# In your service/handler
from typing import Optional
from herpailib.entities.todo import Todo
from herpailib.infrastructure.repository.interfaces import IRepository


class TodoService:
    def __init__(self, repository: IRepository[Todo]):
        self._repository = repository

    async def create_todo(self, task: str) -> Todo:
        return await self._repository.create(task=task)

    async def mark_completed(self, todo_id: str) -> Optional[Todo]:
        return await self._repository.update(todo_id, completed=True)