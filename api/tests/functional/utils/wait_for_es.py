import asyncio
import logging
import os
import sys

from elasticsearch import AsyncElasticsearch

_current = os.path.dirname(os.path.realpath(__file__))
_parent = os.path.dirname(_current)
sys.path.append(_parent)

from settings import settings

PINGS_TO_NOTIFY = 30


async def wait_es():
    es = AsyncElasticsearch(
        hosts=[
            f'{settings.ELASTIC_SCHEME}://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'
        ]
    )
    cnt = 0
    while not await es.ping():
        await asyncio.sleep(1)
        cnt += 1
        if cnt > PINGS_TO_NOTIFY:
            logger.warning("Elastic search no responses for pings.")
            cnt = 0


if __name__ == '__main__':
    logger = logging.getLogger("Ealstic_Waiting")

    logger.info("Try to connect to Elastic search.")
    asyncio.run(wait_es())
    logger.info("Elastic search is ready for work.")
