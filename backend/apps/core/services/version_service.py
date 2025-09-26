"""Centralized version control service."""
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.core.exceptions import VersionConflictError, VersionLockTimeoutError
from ..version_control.adapters import create_version_adapter
from typing import Type, Any, List
import logging

logger = logging.getLogger(__name__)

class VersionService:
    """Centralized version control service using adapters."""
    
    def __init__(self, model_class: Type[Any]):
        self.model_class = model_class
        self.adapter = create_version_adapter(model_class)
        
    @transaction.atomic
    def get_with_version(self, obj_id: int, expected_version: int) -> Any:
        """Get object with version validation."""
        return self.adapter.get_with_version(obj_id, expected_version)

    @transaction.atomic
    def optimistic_update(self, obj: Any, update_fields: List[str]) -> None:
        """Perform optimistic concurrency control update."""
        current_version = obj.version
        obj.version += 1
        updated = self.model_class.objects.filter(
            pk=obj.pk,
            version=current_version
        ).update(**{
            **{f: getattr(obj, f) for f in update_fields},
            'version': obj.version
        })
        
        if not updated:
            raise VersionConflictError(
                f"{self.model_class.__name__} {obj.pk} updated by another process"
            )
            
    @transaction.atomic
    def bulk_optimistic_update(self, objects: List[Any], update_fields: List[str]) -> None:
        """Batch update multiple objects with version checks."""
        for obj in objects:
            self.optimistic_update(obj, update_fields)
