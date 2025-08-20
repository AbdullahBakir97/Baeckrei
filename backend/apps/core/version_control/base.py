"""Base version control utilities without model dependencies."""
from functools import wraps
from django.db import transaction
from django.db import models
from ..exceptions import VersionConflictError, VersionLockTimeoutError
from typing import Any, Callable, Protocol, TypeVar, Generic, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=models.Model)
R = TypeVar('R')

class VersionOperation(Protocol[T, R]):
    """Protocol for version-aware operations using template method pattern."""
    
    def execute(self, obj: T, *args, **kwargs) -> R:
        """
        Template method for versioned operations.
        
        Args:
            obj: Model instance to operate on
            *args: Additional positional arguments for operation
            **kwargs: Additional keyword arguments for operation
            
        Returns:
            Operation result of type R
            
        Raises:
            VersionConflict: If version validation fails
            ValidationError: If operation validation fails
        """
        self._pre_validate(obj)
        result = self._do_operation(obj, *args, **kwargs)
        self._post_update(obj)
        return result
        
    def _pre_validate(self, obj: T) -> None:
        """
        Pre-operation validation.
        
        Args:
            obj: Model instance to validate
            
        Raises:
            ValidationError: If validation fails
        """
        pass
        
    def _do_operation(self, obj: T, *args, **kwargs) -> R:
        """
        Operation implementation.
        
        Args:
            obj: Model instance to operate on
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Operation result of type R
            
        Raises:
            ValidationError: If operation fails
            VersionConflict: If version check fails
        """
        raise NotImplementedError
        
    def _post_update(self, obj: T) -> None:
        """
        Post-operation updates.
        
        Args:
            obj: Model instance that was operated on
        """
        pass

def validate_version(obj: models.Model, expected_version: int) -> None:
    """
    Generic version validation.
    
    Args:
        obj: Object with version attribute to validate
        expected_version: Expected version number
        
    Raises:
        VersionConflict: If versions don't match
    """
    if obj.version != expected_version:
        raise VersionConflict(
            f"Version mismatch: expected {expected_version}, got {obj.version}",
            obj_type=type(obj).__name__,
            obj_id=obj.id
        )

def with_version_lock(model_class: type[models.Model]) -> Callable:
    """
    Generic version lock decorator factory.
    
    Args:
        model_class: The model class to lock
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For class methods, first arg is self, second is the model instance
            if len(args) >= 2 and isinstance(args[1], model_class):
                obj = args[1]
                obj_id = obj.id
                expected_version = obj.version
            else:
                obj_id = kwargs.get('id')
                expected_version = kwargs.get('expected_version')
            
            if not obj_id or expected_version is None:
                raise ValueError("id and expected_version are required")
                
            with transaction.atomic():
                # Use manager method for version-checked locking
                obj = model_class.objects.get_for_update_with_version(obj_id, expected_version)
                result = func(*args, **kwargs)
                
                # Use manager method for version increment
                new_version = model_class.objects.increment_version(obj_id)
                logger.debug(f"{model_class.__name__} {obj_id} version incremented to {new_version}")
                
                return result
        return wrapper
    return decorator
