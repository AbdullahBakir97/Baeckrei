"""Custom JSON encoder for handling special types."""
import json
import uuid
from datetime import datetime
from decimal import Decimal
from django.utils import timezone

class ExtendedJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles additional types."""
    
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (datetime, timezone.datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)
