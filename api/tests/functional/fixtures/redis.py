from typing import Awaitable, Callable

import pytest
import aioredis
from settings import settings


@pytest.fixture(scope="session")
def get_cache_cleaner(redis_client) -> Callable[[None], Awaitable[None]]:
    async def clear_redis():
        await redis_client.flushdb()

    return clear_redis


@pytest.fixture(scope="session")
async def redis_client() -> aioredis.Redis:
    client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    try:
        yield client
    finally:
        await client.close()
