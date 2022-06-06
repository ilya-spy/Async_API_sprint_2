import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from functional.settings import settings
from elasticsearch.helpers import async_bulk as es_bulk
from multidict import CIMultiDictProxy
from testdata.models.genre_factory import GenreFactory


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()



@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="class")
async def fill_es_genre(es_client, redis_client):
    genres = GenreFactory.create(100)
    index_name = ["genres", ]

    _success, failed = await es_bulk(
        es_client,
        index=index_name,
        actions=GenreFactory.from_list_by_one(genres)
    )
    yield genres, failed

    await redis_client.flushdb()
    await es_client.delete_by_query(index=index_name, body={"query": {"match_all": {}}})


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
def request_factory(session):
    async def make_request(method: str,
                           params: Optional[dict] = None) -> HTTPResponse:
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
