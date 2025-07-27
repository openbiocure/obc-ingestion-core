from typing import Type, TypeVar, Dict, Any

T = TypeVar("T")


class Singleton:
    """
    Generic singleton implementation.
    This class allows creating singleton instances of any class.
    """

    _instances: Dict[Type[Any], Any] = {}

    @classmethod
    def get_instance(cls, class_type: Type[T]) -> T:
        """
        Get or create a singleton instance of the specified class.

        Args:
            class_type: The class type to get a singleton instance of

        Returns:
            The singleton instance of the class
        """
        if class_type not in cls._instances:
            cls._instances[class_type] = class_type()
        return cls._instances[class_type]
