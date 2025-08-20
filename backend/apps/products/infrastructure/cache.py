from functools import wraps
from typing import Any, Optional, Callable
from django.core.cache import cache
from django.conf import settings
import hashlib
import json

class CacheService:
    """Service for handling caching operations"""
    
    DEFAULT_TIMEOUT = 3600  # 1 hour

    @staticmethod
    def make_key(prefix: str, *args, **kwargs) -> str:
        """Create a unique cache key based on arguments"""
        key_dict = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_dict, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    @staticmethod
    def cache_decorator(prefix: str, timeout: Optional[int] = None) -> Callable:
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Skip caching if DEBUG mode is on
                if settings.DEBUG:
                    return func(*args, **kwargs)

                # Create cache key
                cache_key = CacheService.make_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Calculate result and cache it
                result = func(*args, **kwargs)
                cache_timeout = timeout or CacheService.DEFAULT_TIMEOUT
                cache.set(cache_key, result, timeout=cache_timeout)
                
                return result
            return wrapper
        return decorator

    @staticmethod
    def invalidate_prefix(prefix: str) -> None:
        """Invalidate all cache keys with given prefix"""
        if not settings.DEBUG:
            cache.delete_pattern(f"{prefix}:*")

class ProductCache:
    """Product-specific cache operations"""
    
    PREFIX = "product"
    
    @staticmethod
    def get_product(product_id: int) -> Optional[dict]:
        key = f"{ProductCache.PREFIX}:{product_id}"
        return cache.get(key)

    @staticmethod
    def set_product(product_id: int, data: dict) -> None:
        key = f"{ProductCache.PREFIX}:{product_id}"
        cache.set(key, data, timeout=CacheService.DEFAULT_TIMEOUT)

    @staticmethod
    def invalidate_product(product_id: int) -> None:
        key = f"{ProductCache.PREFIX}:{product_id}"
        cache.delete(key)

class CategoryCache:
    """Category-specific cache operations"""
    
    PREFIX = "category"
    
    @staticmethod
    def get_category_tree() -> Optional[dict]:
        return cache.get(f"{CategoryCache.PREFIX}:tree")

    @staticmethod
    def set_category_tree(tree: dict) -> None:
        cache.set(
            f"{CategoryCache.PREFIX}:tree",
            tree,
            timeout=CacheService.DEFAULT_TIMEOUT
        )

    @staticmethod
    def invalidate_tree() -> None:
        cache.delete(f"{CategoryCache.PREFIX}:tree")
