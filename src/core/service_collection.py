from typing import TypeVar, Type, Dict, Any, Optional, Callable
import inspect

T = TypeVar('T')

class ServiceCollection:
    """
    Container for service registration and resolution.
    This class manages singletons, scoped, and transient services.
    """
    
    def __init__(self):
        """Initialize a new service collection."""
        self._services = {}
        self._scoped_factories = {}
        self._transient_factories = {}
    
    def add_singleton(self, interface_type: Type[T], implementation):
        """
        Register a singleton service.
        
        Args:
            interface_type: The interface or type to register
            implementation: The implementation type, instance, or factory
        """
        if callable(implementation) and not isinstance(implementation, type):
            # Factory function
            instance = implementation()
            self._services[interface_type] = instance
        else:
            # Type or instance
            if isinstance(implementation, type):
                instance = implementation()
            else:
                instance = implementation
            self._services[interface_type] = instance
    
    def add_scoped(self, interface_type: Type[T], implementation_factory):
        """
        Register a scoped service factory.
        
        Args:
            interface_type: The interface or type to register
            implementation_factory: The implementation factory
        """
        if isinstance(implementation_factory, type):
            factory = implementation_factory
        else:
            factory = implementation_factory
        self._scoped_factories[interface_type] = factory
    
    def add_transient(self, interface_type: Type[T], implementation_factory):
        """
        Register a transient service factory.
        
        Args:
            interface_type: The interface or type to register
            implementation_factory: The implementation factory
        """
        if isinstance(implementation_factory, type):
            factory = implementation_factory
        else:
            factory = implementation_factory
        self._transient_factories[interface_type] = factory
    
    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """
        Get a registered service.
        
        Args:
            service_type: The type of service to resolve
            
        Returns:
            The resolved service or None if not found
        """
        service = self._services.get(service_type)
        if service is not None:
            return service
        
        # If it's a scoped service, we need a scope
        if service_type in self._scoped_factories:
            raise ValueError(f"Service {service_type.__name__} is scoped and requires a ServiceScope")
        
        # If it's a transient service, create a new instance
        if service_type in self._transient_factories:
            factory = self._transient_factories[service_type]
            if inspect.isclass(factory):
                return factory()
            else:
                return factory()
        
        return None
