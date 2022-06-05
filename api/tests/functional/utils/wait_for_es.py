import asyncio
from contextlib import asynccontextmanager
import logging
import os
import sys
from typing import Generator

from elasticsearch import AsyncElasticsearch

_current = os.path.dirname(os.path.realpath(__file__))
_parent = os.path.dirname(_current)
sys.path.append(_parent)

from settings import settings
from wait_for_base import ConnectChecker, wait as base_wait


@asynccontextmanager
async def get_es() -> Generator[AsyncElasticsearch, None, None]:
    es = AsyncElasticsearch(hosts=[f'{settings.ELASTIC_SCHEME}://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'])
    try:
        yield es
    finally:
        await es.close()


class EsChecker(ConnectChecker):
    def __init__(self, es: AsyncElasticsearch):
        self._client = es

    def __repr__(self):
        return "Elastic Search"

    async def ping(self) -> bool:
        return await self._client.ping()


async def wait_es():
    async with get_es() as es:
        await base_wait(EsChecker(es), logging.getLogger("Elastic_Waiting"))


if __name__ == '__main__':
    asyncio.run(wait_es())
