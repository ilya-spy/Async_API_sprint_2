import asyncio

from dataclasses import dataclass
from typing import Awaitable, Optional, Callable

import aiohttp
import pytest

from multidict import CIMultiDictProxy
from settings import settings

pytest_plugins = ("fixtures.redis", "fixtures.elastic", "fixtures.genre", "fixtures.person")


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="class")
async def backend_cleaner(get_es_cleaner, get_cache_cleaner) -> Callable:
    async def inner(index):
        # clear all db/index data after class tests done
        await get_es_cleaner(index)
        await get_cache_cleaner()

    return inner


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


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
