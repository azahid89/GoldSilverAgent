"""
Simple in-memory cache for API responses
"""
from datetime import datetime, timedelta
from typing import Any, Optional
import threading

class SimpleCache:
    """Thread-safe in-memory cache with TTL"""
    
    def __init__(self, default_ttl_seconds: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl_seconds
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if datetime.now() < expiry:
                    return value
                else:
                    # Expired, remove it
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache with TTL"""
        with self.lock:
            ttl = ttl_seconds or self.default_ttl
            expiry = datetime.now() + timedelta(seconds=ttl)
            self.cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()

# Global cache instance
cache = SimpleCache(default_ttl_seconds=300)  # 5 minutes





