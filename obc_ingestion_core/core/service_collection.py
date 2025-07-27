import inspect
from typing import Optional, Type, TypeVar, Any, Dict

T = TypeVar("T")


class ServiceCollection:
    """
    Container for service registration and resolution.
    This class manages singletons, scoped, and transient services.
    """

    def __init__(self) -> None:
        """Initialize a new service collection."""
        self._services: Dict[Any, Any] = {}
        self._scoped_factories: Dict[Any, Any] = {}
        self._transient_factories: Dict[Any, Any] = {}

    def add_singleton(self, interface_type: Any, implementation):
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

    def get_service(self, service_type: Any) -> Optional[Any]:
        """
        Get a registered service.

        Args:
            service_type: The type of service to resolve

        Returns:
            The resolved service or None if not found
        """
        service = self._services.get(service_type)
        if service is not None:
            # Check if it's a factory function and call it if it is
            if callable(service) and not isinstance(service, type):
                return service()
            return service

        # If it's a scoped service, we need a scope
        if service_type in self._scoped_factories:
            raise ValueError(
                f"Service {service_type.__name__} is scoped and requires a ServiceScope"
            )

        # If it's a transient service, create a new instance
        if service_type in self._transient_factories:
            factory = self._transient_factories[service_type]
            if inspect.isclass(factory):
                return factory()
            else:
                return factory()

        return None
