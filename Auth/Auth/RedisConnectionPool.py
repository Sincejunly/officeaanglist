import asyncio
import asyncio_redis

class RedisConnectionPool:
    def __init__(self, host='localhost', port=6379, password='123456', poolsize=10):
        self.host = host
        self.port = port
        self.poolsize = poolsize
        self.connection = None
        self.password = password

    async def connect(self):
        self.connection = await asyncio_redis.Pool.create(
            host=self.host, port=self.port, poolsize=self.poolsize, password=self.password
        )

    # async def close(self):
    #     if self.connection is not None:
    #         self.connection.close()
    #         await self.connection.wait_closed()
    #         self.connection = None

    async def insert(self, key, value, expiration=None):
        transaction = await self.connection.multi()
        f = await transaction.set(key, value)
        
        if expiration is not None:
            await transaction.expire(key, expiration)
        
        await transaction.exec()
        return await f

    async def query(self, key):
        return await self.connection.get(key)

    async def delete(self, *keys):
        return await self.connection.delete(*keys)