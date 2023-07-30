# views.py
import os
import aioredis
from django.http import HttpResponse, JsonResponse
from channels.db import database_sync_to_async
from .settings import BASE_DIR

from .readjson import read_json


# async def redisPool():
#     from .RedisConnectionPool import RedisConnectionPool
#     data = await read_json(os.path.join(os.path.dirname(BASE_DIR), 'data.json'))

#     redis = RedisConnectionPool(data['serverHost'],password='159756')
#     await redis.connect()
#     return redis

async def async_example(request):
    redis_pool = request.middleware['RedisPool'].redis_pool
    print(await redis_pool.query('test', 'test2'))
    return HttpResponse("Async Response")


async def test(request):
    global cache,ddd
    print(ddd)
    #await cache.insert('test', 'test2')
    print(await cache.get('test'))
    data = {'message': 'This is an async response'}
    return JsonResponse(data)