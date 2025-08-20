"""Utilities for generating identifiers."""
import hashlib
import time
import uuid

def generate_cart_id() -> str:
    """
    Generate a unique cart identifier.
    
    Returns:
        32-character hexadecimal string
    """
    unique_string = f"{uuid.uuid4()}{time.time()}"
    return hashlib.md5(unique_string.encode()).hexdigest()
