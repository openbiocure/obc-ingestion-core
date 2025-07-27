
# Define a Todo entity
from obc_ingestion_core.data.entity import BaseEntity
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column


class Todo(BaseEntity):
    """Todo entity for task management."""
    __tablename__ = "todos"
    
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)
