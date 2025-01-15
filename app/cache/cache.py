import redis
from typing import Optional, Dict
import json

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        
    def get_product(self, product_title: str) -> Optional[Dict]:
        data = self.redis_client.get(product_title)
        return json.loads(data) if data else None
        
    def save_product(self, product_title: str, product_data: Dict, expire_time: int = 3600):
        self.redis_client.setex(
            product_title,
            expire_time,
            json.dumps(product_data)
        )
