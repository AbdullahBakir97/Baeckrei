"""Core exceptions for version control."""

class VersionError(Exception):
    """Base exception for version-related errors."""
    pass

class VersionConflictError(VersionError):
    """Base version conflict exception."""
    def __init__(self, message="Version conflict detected", obj_type: str = None, obj_id: int = None):
        self.obj_type = obj_type
        self.obj_id = obj_id
        detail = message
        if obj_type and obj_id:
            detail += f" | Object: {obj_type} ID: {obj_id}"
        super().__init__(detail)

class VersionLockTimeoutError(VersionError):
    """Base version lock timeout exception."""
    def __init__(self, obj_type: str, obj_id: int):
        super().__init__(f"Timeout acquiring lock for {obj_type} {obj_id}")
