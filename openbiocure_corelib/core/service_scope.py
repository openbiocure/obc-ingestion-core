from typing import TypeVar, Type, Dict, Any
import inspect
from .interfaces import IServiceScope

T = TypeVar('T')

class ServiceScope(IServiceScope):
    """
    Scoped service container that provides isolated service instances.
    """
    
    def __init__(self, engine):
        """
        Initialize a service scope.
        
        Args:
            engine: The parent engine that created this scope
        """
        self._engine = engine
        self._scoped_services = {}
    
    def resolve(self, type_: Type[T]) -> T:
        """
        Resolve a service from the scope.
        
        Args:
            type_: The type of service to resolve
            
        Returns:
            The resolved service
        """
        # Check if we have the service in this scope
        service = self._scoped_services.get(type_)
        if service is not None:
            return service
        
        # Check if it's a scoped service
        factory = self._engine._services._scoped_factories.get(type_)
        if factory is not None:
            if inspect.isclass(factory):
                service = factory()
            else:
                service = factory()
            self._scoped_services[type_] = service
            return service
        
        # Otherwise, delegate to the engine
        return self._engine.resolve(type_)
    
    async def dispose(self) -> None:
        """Dispose the scope and release all resources."""
        # Clean up resources
        for service in self._scoped_services.values():
            if hasattr(service, 'dispose') and callable(service.dispose):
                await service.dispose()
        self._scoped_services.clear()
