"""Generic event logging base class for application-wide events."""
from django.db import models
from typing import Any, Dict, Optional, Type
from django.core.exceptions import ValidationError
from ..utils.json_encoder import ExtendedJSONEncoder
import logging
import json

logger = logging.getLogger(__name__)

class BaseEventLogger:
    """Base event logger for generic event logging across the application."""
    
    def __init__(self, event_model: Type[models.Model]):
        """
        Initialize base event logger.
        
        Args:
            event_model: Event model class to use for logging
        """
        self.event_model = event_model
        
    def log(self, event_type: str, related_object: models.Model,
            details: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None) -> models.Model:
        """
        Log a generic event.
        
        Args:
            event_type: Type of event
            related_object: Related model instance
            details: Optional event details
            metadata: Optional event metadata
            
        Returns:
            Created event instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Convert details to JSON string to ensure it's valid JSON
            details_json = json.dumps(details or {}, cls=ExtendedJSONEncoder)
            metadata_json = json.dumps(metadata or {}, cls=ExtendedJSONEncoder)

            event = self.event_model(
                event_type=event_type,
                details=json.loads(details_json),
                metadata=json.loads(metadata_json)
            )
            
            # Set the related object based on model name
            setattr(event, related_object._meta.model_name.lower(), related_object)
            
            event.full_clean()
            event.save()
            return event
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in event details/metadata: {str(e)}")
            raise ValidationError("Event details/metadata must be valid JSON")
        except Exception as e:
            logger.error(f"Error logging event: {str(e)}")
            raise ValidationError(str(e))
