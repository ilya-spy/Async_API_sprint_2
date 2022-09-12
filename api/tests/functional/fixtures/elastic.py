from typing import Awaitable, Callable
from elasticsearch.helpers import async_bulk
from elasticsearch import AsyncElasticsearch

import pytest
from settings import settings


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts=[f"{settings.ELASTIC_SCHEME}://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture(scope="session")
def es_bulk():
    # issue bukl method for clients to fill backend data
    return async_bulk


@pytest.fixture(scope="session")
def get_es_cleaner(es_client) -> Callable[[str], Awaitable[None]]:
    async def clear_es(index: str):
        await es_client.indices.refresh()
        await es_client.delete_by_query(index=index, query={"match_all": {}}, refresh=True)

    return clear_es


@pytest.fixture(scope="session")
def get_es_updater(es_client) -> Callable[[str, str, dict[str, str]], Awaitable[None]]:
    async def updater(index: str, doc_id: str, fields: dict[str, str]):
        await es_client.update(index=index, id=doc_id, doc=fields, refresh=True)

    return updater
