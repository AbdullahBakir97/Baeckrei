from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from django.db.models import Model, QuerySet
from django.core.exceptions import ValidationError
from django.db import transaction

T = TypeVar('T', bound=Model)

class BaseService(Generic[T]):
    """Base service class for common CRUD operations with validation and error handling."""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
    
    def get_queryset(self) -> QuerySet[T]:
        """Get the base queryset for the model."""
        return self.model_class.objects.all()
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get a single instance by ID with error handling."""
        try:
            return self.get_queryset().get(id=id)
        except self.model_class.DoesNotExist:
            return None
    
    def list(self, filters: Dict[str, Any] = None, order_by: List[str] = None) -> QuerySet[T]:
        """Get a filtered and ordered queryset of instances."""
        queryset = self.get_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        if order_by:
            queryset = queryset.order_by(*order_by)
        return queryset
    
    @transaction.atomic
    def create(self, **data) -> T:
        """Create a new instance with validation."""
        try:
            instance = self.model_class(**data)
            instance.full_clean()
            instance.save()
            return instance
        except ValidationError as e:
            raise ValidationError(f"Validation error during creation: {str(e)}")
    
    @transaction.atomic
    def update(self, instance: T, **data) -> T:
        """Update an instance with validation."""
        try:
            for key, value in data.items():
                setattr(instance, key, value)
            instance.full_clean()
            instance.save()
            return instance
        except ValidationError as e:
            raise ValidationError(f"Validation error during update: {str(e)}")
    
    @transaction.atomic
    def delete(self, instance: T) -> bool:
        """Delete an instance."""
        try:
            instance.delete()
            return True
        except Exception as e:
            raise Exception(f"Error during deletion: {str(e)}")
    
    def exists(self, **filters) -> bool:
        """Check if instances matching the filters exist."""
        return self.get_queryset().filter(**filters).exists()
    
    def count(self, **filters) -> int:
        """Count instances matching the filters."""
        return self.get_queryset().filter(**filters).count()
    
    def bulk_create(self, instances: List[T]) -> List[T]:
        """Bulk create instances."""
        return self.model_class.objects.bulk_create(instances)
    
    def bulk_update(self, instances: List[T], fields: List[str]) -> None:
        """Bulk update instances."""
        self.model_class.objects.bulk_update(instances, fields)
