from typing import TypeVar, Generic, Protocol, Any

T = TypeVar('T')

class ISpecification(Generic[T], Protocol):
    def is_satisfied_by(self, entity: T) -> bool: ...
    def to_expression(self) -> Any: ...

class Specification(Generic[T], ISpecification[T]):
    def is_satisfied_by(self, entity: T) -> bool:
        # Default implementation
        raise NotImplementedError
    
    def to_expression(self) -> Any:
        # Convert to SQLAlchemy expression
        raise NotImplementedError
    
    def and_(self, other: ISpecification[T]) -> 'ISpecification[T]':
        return AndSpecification(self, other)
    
    def or_(self, other: ISpecification[T]) -> 'ISpecification[T]':
        return OrSpecification(self, other)

class AndSpecification(Generic[T], Specification[T]):
    def __init__(self, left: ISpecification[T], right: ISpecification[T]):
        self._left = left
        self._right = right
    
    def is_satisfied_by(self, entity: T) -> bool:
        return self._left.is_satisfied_by(entity) and self._right.is_satisfied_by(entity)
    
    def to_expression(self) -> Any:
        return self._left.to_expression() & self._right.to_expression()

class OrSpecification(Generic[T], Specification[T]):
    def __init__(self, left: ISpecification[T], right: ISpecification[T]):
        self._left = left
        self._right = right
    
    def is_satisfied_by(self, entity: T) -> bool:
        return self._left.is_satisfied_by(entity) or self._right.is_satisfied_by(entity)
    
    def to_expression(self) -> Any:
        return self._left.to_expression() | self._right.to_expression()
