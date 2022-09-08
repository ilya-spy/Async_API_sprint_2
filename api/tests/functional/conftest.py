import asyncio

from dataclasses import dataclass
from typing import Awaitable, Optional, Callable

import aiohttp
import aioredis
import pytest

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from multidict import CIMultiDictProxy
from settings import settings


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def es_bulk():
    # issue bukl method for clients to fill backend data
    return async_bulk


@pytest.fixture(scope="session")
def get_cache_cleaner(redis_client) -> Callable[[None], Awaitable[None]]:
    async def clear_redis():
        await redis_client.flushdb()

    return clear_redis


@pytest.fixture(scope="session")
def get_es_cleaner(es_client) -> Callable[[str], Awaitable[None]]:
    async def clear_es(index: str):
        await es_client.indices.refresh()
        await es_client.delete_by_query(index=index, query={"match_all": {}}, refresh=True)

    return clear_es


@pytest.fixture(scope="class")
async def backend_cleaner(get_es_cleaner, get_cache_cleaner) -> Callable:
    async def inner(index):
        # clear all db/index data after class tests done
        await get_es_cleaner(index)
        await get_cache_cleaner()

    return inner


@pytest.fixture(scope="session")
def get_es_updater(es_client) -> Callable[[str, str, dict[str, str]], Awaitable[None]]:
    async def updater(index: str, doc_id: str, fields: dict[str, str]):
        await es_client.update(index=index, id=doc_id, doc=fields, refresh=True)

    return updater


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts=[f"{settings.ELASTIC_SCHEME}://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture(scope="session")
async def redis_client() -> aioredis.Redis:
    client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def http_requester(session) -> Callable[[str, Optional[dict]], Awaitable[HTTPResponse]]:
    async def requester_factory(endpoint: str, params: Optional[dict] = None) -> HTTPResponse:
        extra = {'sort': 'id'}
        if params:
            extra.update(params)

        # в боевых системах старайтесь так не делать!
        url = f"{settings.API_SCHEME}://{settings.API_HOST}:{settings.API_PORT}/api/v1/{endpoint}"

        async with session.get(url, params=extra) as response:
            response_body = await response.json()

            return HTTPResponse(
                body=response_body,
                headers=response.headers,
                status=response.status,
            )

    return requester_factory
