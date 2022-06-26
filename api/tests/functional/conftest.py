import asyncio
from dataclasses import dataclass
from typing import Optional, Awaitable, Callable, AsyncGenerator

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk as es_bulk
from multidict import CIMultiDictProxy
from settings import settings
from testdata.models.genre_factory import GenreFactory
from testdata.schemes.v1.genre import Genre

_GENRES_COUNT = 100


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module")
async def fill_es_genre(es_client, get_es_cleaner, get_cache_cleaner) -> AsyncGenerator[(Genre, list[Genre])]:
    genres = GenreFactory.create(_GENRES_COUNT)
    index_name = ["genres", ]
    # clear all other data for genres
    await get_es_cleaner(index_name[0])
    await get_cache_cleaner()

    _success, failed = await es_bulk(
        es_client,
        index=index_name,
        actions=GenreFactory.from_list_by_one(genres)
    )
    await es_client.indices.refresh()
    try:
        yield genres, failed
    finally:
        await get_cache_cleaner()
        await get_es_cleaner(index_name[0])


@pytest.fixture(scope="session")
def get_es_cleaner(es_client) -> Callable[[str], Awaitable[None]]:
    async def clear_es(index: str):
        await es_client.indices.refresh()
        await es_client.delete_by_query(index=index, query={"match_all": {}})

    return clear_es


@pytest.fixture
async def no_cache(redis_client):
    await redis_client.flushdb()
    yield
    await redis_client.flushdb()


@pytest.fixture(scope="session")
def get_cache_cleaner(redis_client) -> Callable[[None], Awaitable[None]]:
    async def clear_redis():
        await redis_client.flushdb()

    return clear_redis


@pytest.fixture(scope="session")
def get_es_entry_updater(es_client) -> Callable[[str, str, dict[str, str]], Awaitable[None]]:
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
def request_factory(session) -> Callable[[str, Optional[dict]], Awaitable[HTTPResponse]]:
    async def make_request(endpoint: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        # в боевых системах старайтесь так не делать!
        url = f"{settings.API_SCHEME}://{settings.API_HOST}:{settings.API_PORT}/api/v1/{endpoint}"

        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return make_request
