import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Generator

import aioredis
from aioredis import Redis
from aioredis import exceptions as rd_exp

_current = os.path.dirname(os.path.realpath(__file__))
_parent = os.path.dirname(_current)
sys.path.append(_parent)

from settings import settings
from wait_for_base import ConnectChecker
from wait_for_base import wait as base_wait


@asynccontextmanager
async def get_rds() -> Generator[Redis, None, None]:
    rds = aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}')
    try:
        yield rds
    finally:
        await rds.close()


class RedisChecker(ConnectChecker):
    def __init__(self, rds: Redis, logger: logging.Logger):
        self._client = rds
        self._log = logger

    def __repr__(self):
        return "Redis"

    async def ping(self) -> bool:
        try:
            await self._client.ping()
        except (rd_exp.ConnectionError, rd_exp.TimeoutError):
            pass
        except Exception:
            self._log.exception("Unexpected exception.")
        else:
            return True
        return False


async def wait_rds():
    async with get_rds() as rds:
        log = logging.getLogger("Redis_Waiting")
        await base_wait(RedisChecker(rds, log), log)


if __name__ == '__main__':
    asyncio.run(wait_rds())
