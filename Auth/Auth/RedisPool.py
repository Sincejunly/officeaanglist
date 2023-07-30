# myapp/apps.py

import os

from .settings import BASE_DIR
from .RedisConnectionPool import RedisConnectionPool
import asyncio

from .readjson import read_json

class RedisPool:
    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        await self.setup_redis_pool()
        response = await self.get_response(request)
        return response

    async def setup_redis_pool(self):
        if not hasattr(self, 'redis_pool'):
            data = await read_json(os.path.join(os.path.dirname(BASE_DIR), 'data.json'))
            self.redis_pool = RedisConnectionPool(data['serverHost'], password='159756')
            await self.redis_pool.connect()
