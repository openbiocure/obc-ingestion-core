class HerpAILibException(Exception):
    """Base exception for all HerpAI-Lib exceptions."""
    pass

class ServiceNotFoundException(HerpAILibException):
    """Exception raised when a service is not found."""
    pass

class RepositoryException(HerpAILibException):
    """Exception raised for repository-related errors."""
    pass

class EntityNotFoundException(RepositoryException):
    """Exception raised when an entity is not found."""
    pass

class DatabaseException(HerpAILibException):
    """Exception raised for database-related errors."""
    pass
