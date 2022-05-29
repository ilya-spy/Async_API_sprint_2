import json
import logging
from typing import Optional

from aioredis import Redis
from pydantic import BaseModel

from etl import state


class CacheIndex(BaseModel):
    values: list[dict]


class CacheAPI:
    def __init__(self, index: str, redis: Redis) -> None:
        self.index = index
        self.redis = redis
        self.logger = logging.getLogger("CacheAPI: " + index)
        self.storage = state.RedisStorage(self.redis, name=self.index)

    async def sync_state(self):
        try:
            self.state = await self.storage.retrieve_state()
        except Exception:
            self.logger.info("State not cached, init...")
            self.state = {}

    async def get_single(self, key: str) -> Optional[object]:
        await self.sync_state()
        if key in self.state:
            self.logger.debug('Redis state key obj: %s' % (self.state[key]))
        return json.loads(self.state[key]) if key in self.state else None

    async def put_single(self, key: str, obj: BaseModel) -> None:
        await self.sync_state()
        self.state[key] = obj.json()
        self.logger.debug('Redis state put obj: ' + str(self.state))
        await self.storage.save_state(self.state)

    async def get_index(self, index: str, key: str) -> list[Optional[dict]]:
        result = await self.get_single('_'.join([index, key]))
        return CacheIndex(**result).values if result else None

    async def put_index(self, index: str, key: str, data: list[dict]) -> None:
        await self.put_single('_'.join([index, key]), CacheIndex(values=data))

    async def drop_index(self, index, key: str) -> int:
        pass
