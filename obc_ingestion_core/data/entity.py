from datetime import UTC, datetime
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseEntity(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    tenant_id: Mapped[Optional[str]] = mapped_column(default=None)
