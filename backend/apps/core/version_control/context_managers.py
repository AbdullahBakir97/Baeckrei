"""Context managers for version-controlled operations."""
from django.db import transaction
from typing import Type, Any, TypeVar
from ..services.version_service import VersionService
from ..exceptions import VersionConflictError, VersionLockTimeoutError
from .adapters import create_version_adapter, VersionAdapterProtocol
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class VersionAwareTransaction:
    """Context manager for version-controlled transactions."""
    
    def __init__(self, model_class: Type[T], obj_id: int, expected_version: int):
        """
        Initialize version-aware transaction.
        
        Args:
            model_class: Model class to operate on
            obj_id: Object ID
            expected_version: Expected version number
        """
        self.model_class = model_class
        self.obj_id = obj_id
        self.expected_version = expected_version
        self.adapter: VersionAdapterProtocol = create_version_adapter(model_class)
        
    def __enter__(self) -> T:
        """
        Enter the context, acquiring version lock.
        
        Returns:
            Model instance with version check
            
        Raises:
            VersionConflict: If version mismatch
        """
        try:
            self.obj = self.adapter.get_with_version(
                self.obj_id, 
                self.expected_version
            )
            return self.obj
            
        except Exception as e:
            logger.error(
                f"Failed to acquire version lock for {self.model_class.__name__} "
                f"{self.obj_id}: {str(e)}"
            )
            raise
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context, releasing lock and incrementing version if no error.
        
        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        if not exc_type:
            try:
                # Only increment version if no exception occurred
                self.adapter.increment_version(self.obj_id)
            except Exception as e:
                logger.error(
                    f"Failed to release version lock for {self.model_class.__name__} "
                    f"{self.obj_id}: {str(e)}"
                )
                raise