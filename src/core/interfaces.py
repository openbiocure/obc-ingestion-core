from typing import TypeVar, Type, Protocol

T = TypeVar('T')

class IServiceScope(Protocol):
    """Interface for a service scope."""
    
    def resolve(self, type_: Type[T]) -> T: ...
    
    async def dispose(self) -> None: ...

class IEngine(Protocol):
    """Interface for the application engine."""
    
    @property
    def current(self) -> 'IEngine': ...
    
    def start(self) -> None: ...
    
    def resolve(self, type_: Type[T]) -> T: ...
    
    def create_scope(self) -> IServiceScope: ...
    
    def register(self, interface_type: Type[T], implementation) -> None: ...
