from herpailib.infrastructure.db.base_entity import BaseEntity
from sqlalchemy.orm import Mapped, mapped_column

class Todo(BaseEntity):
    __tablename__ = "todos"
    
    task: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)
    
    # Usage with dependency injection
    # from dependency_injector import containers, providers
    # from sqlalchemy.ext.asyncio import AsyncSession

    # class Container(containers.DeclarativeContainer):
    #     db_session = providers.Dependency(AsyncSession)
        
    #     todo_repository = providers.Factory(
    #         BaseRepository[Todo],
    #         db=db_session,
    #         entity=Todo
    #     )