import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Generator

from elasticsearch import AsyncElasticsearch
from elasticsearch import logger as es_logger
from functional.settings import settings
from wait_for_base import ConnectChecker, backoff


@asynccontextmanager
async def get_es() -> Generator[AsyncElasticsearch, None, None]:
    es = AsyncElasticsearch(hosts=[
        f'{settings.ELASTIC_SCHEME}://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'
    ])
    try:
        yield es
    finally:
        await es.close()


class EsChecker(ConnectChecker):
    def __init__(self, es: AsyncElasticsearch):
        super().__init__(logging.getLogger("Elastic_Waiting"))
        self.client = es

    @backoff('Elastic Search')
    async def ping(self) -> bool:
        return await self.client.ping()


async def wait_for_elastic():
    async with get_es() as es:
        checker = EsChecker(es)
        await checker.ping()

if __name__ == '__main__':
    es_logger.setLevel("ERROR")
    asyncio.run(wait_for_elastic())
