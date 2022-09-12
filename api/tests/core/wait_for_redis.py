import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Generator

import aioredis
from aioredis import Redis
from functional.settings import settings
from wait_for_base import ConnectChecker, backoff


@asynccontextmanager
async def get_rds() -> Generator[Redis, None, None]:
    rds = aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}')
    try:
        yield rds
    finally:
        await rds.close()


class RedisChecker(ConnectChecker):
    def __init__(self, rds: Redis):
        super().__init__(logging.getLogger("Elastic_Waiting"))
        self.client: Redis = rds

    @backoff("Redis cache")
    async def ping(self) -> bool:
        return await self.client.ping()


async def wait_for_redis():
    async with get_rds() as rds:
        checker = RedisChecker(rds)
        await checker.ping()


if __name__ == '__main__':
    asyncio.run(wait_for_redis())
