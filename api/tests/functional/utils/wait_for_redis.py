import asyncio
import logging
import sys

import aioredis
from aioredis import exceptions as rd_exp

# FixMe remove this dirty hack
sys.path.append('../functional')

from settings import settings

PINGS_TO_NOTIFY = 30


async def wait():
    rd = aioredis.from_url(
        f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}')
    cnt = 0

    while True:
        try:
            await rd.ping()
        except (rd_exp.ConnectionError, rd_exp.TimeoutError):
            pass
        except Exception:
            logger.exception("Unexpected exception.")
        else:
            break
        # handle exceptions
        await asyncio.sleep(1)
        cnt += 1
        if cnt > PINGS_TO_NOTIFY:
            logger.warning("Redis no pings responses.")
            cnt = 0


if __name__ == '__main__':
    logger = logging.getLogger("Redis Waiting")
    logger.info("Try to connect to Redis search.")
    asyncio.run(wait())
    logger.info("Redis is ready for work.")
