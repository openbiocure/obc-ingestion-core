from typing import Any, Protocol, Type, TypeVar

T = TypeVar("T")


class IServiceScope(Protocol):
    """Interface for a service scope."""

    def resolve(self, type_: Type[T]) -> T: ...

    async def dispose(self) -> None: ...


class IEngine(Protocol):
    """Interface for the application engine."""

    @property
    def config(self) -> Any: ...

    @classmethod
    def current(cls) -> "IEngine": ...

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    def resolve(self, type_: Type[T]) -> T: ...

    def create_scope(self) -> IServiceScope: ...

    def register(self, interface_type: Type[T], implementation) -> None: ...
