from typing import TypeVar, Generic, Type
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)

class BaseService(Generic[T]):
    """Base service class for common CRUD operations."""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
    
    def get_queryset(self) -> QuerySet[T]:
        """Get the base queryset for the model."""
        return self.model_class.objects.all()
    
    def get_by_id(self, id) -> T:
        """Get a single instance by ID."""
        return self.get_queryset().get(id=id)
    
    def list(self, **filters) -> QuerySet[T]:
        """Get a filtered queryset of instances."""
        return self.get_queryset().filter(**filters)
    
    def create(self, **data) -> T:
        """Create a new instance."""
        instance = self.model_class(**data)
        instance.full_clean()
        instance.save()
        return instance
    
    def update(self, instance: T, **data) -> T:
        """Update an existing instance."""
        for key, value in data.items():
            setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        return instance
    
    def delete(self, instance: T) -> None:
        """Delete an instance."""
        instance.delete()
