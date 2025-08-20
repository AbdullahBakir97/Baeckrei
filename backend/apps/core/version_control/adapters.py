"""Version control adapters for different model types."""
from typing import Generic, TypeVar, Protocol
from django.db import models
from ..exceptions import VersionConflictError, VersionLockTimeoutError

ModelType = TypeVar('ModelType', bound=models.Model)

class VersionAdapterProtocol(Protocol[ModelType]):
    """Protocol for version control adapters."""
    
    def get_with_version(self, obj_id: int, expected_version: int) -> ModelType:
        ...
        
    def increment_version(self, obj_id: int) -> int:
        ...

class GenericVersionAdapter(Generic[ModelType]):
    """Generic version control adapter for models."""
    
    def __init__(self, model_class: type[ModelType]):
        self.model_class = model_class
    
    def get_with_version(self, obj_id: int, expected_version: int) -> ModelType:
        """Get object with version validation."""
        obj = self.model_class.objects.get(pk=obj_id)
        if obj.version != expected_version:
            raise VersionConflict(
                f"{self.model_class.__name__} version mismatch",
                obj_type=self.model_class.__name__,
                obj_id=obj_id
            )
        return obj
    
    def increment_version(self, obj_id: int) -> int:
        """Atomically increment version."""
        self.model_class.objects.filter(pk=obj_id).update(version=models.F('version') + 1)
        return self.model_class.objects.get(pk=obj_id).version

def create_version_adapter(model_class: type[ModelType]) -> VersionAdapterProtocol:
    """Factory function for version adapters."""
    return GenericVersionAdapter(model_class)
