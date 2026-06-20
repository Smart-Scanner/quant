"""Cache layer for API responses."""

import time
from typing import Any, Optional, Callable
from datetime import datetime, timedelta

class CacheLayer:
    """In-memory TTL cache for API responses."""
    
    def __init__(self):
        self.cache = {}
        self.ttl_map = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key not in self.cache:
            return None
        
        expiry = self.ttl_map.get(key)
        if expiry and datetime.now() > expiry:
            del self.cache[key]
            del self.ttl_map[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set cached value with TTL."""
        self.cache[key] = value
        self.ttl_map[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def warm_status_cache(self, compute_fn: Callable):
        """Warm up status cache on startup."""
        try:
            status = compute_fn()
            self.set("status", status, ttl_seconds=5)
        except Exception as e:
            print(f"Cache warmup error: {e}")

cache_layer = CacheLayer()
