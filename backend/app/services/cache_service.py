# backend/app/services/cache_service.py
import redis
import json
from typing import Any, Optional
from app.config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL):
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except:
            return False

cache = CacheService()