import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Generator

import aioredis
from aioredis import Redis
from aioredis import exceptions as rd_exp
from functional.logger import logger
from functional.settings import settings
from wait_for_base import ConnectChecker


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

    def __repr__(self):
        return "Redis cache"

    async def ping(self) -> bool:
        logger.info("Pinging redis cacher...")
        try:
            await self.client.ping()
        except (rd_exp.ConnectionError, rd_exp.TimeoutError):
            pass
        except Exception:
            logger.exception("Unexpected exception.")
        else:
            return True
        return False


async def wait_for_redis():
    async with get_rds() as rds:
        checker = RedisChecker(rds)
        await checker.wait()


if __name__ == '__main__':
    asyncio.run(wait_for_redis())
