import json
import logging
from typing import Optional
from uuid import UUID

from aioredis import Redis
from pydantic import BaseModel

from interfaces.cache import CacheAPI, CacheIndex


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class RedisCacher(CacheAPI):
    """Redis-based cacher service implementation"""

    @classmethod
    def decode_redis(cls, src):
        """Decode redis bytes streams into Python structs"""

        if isinstance(src, list):
            rv = list()
            for key in src:
                rv.append(cls.decode_redis(key))
            return rv
        elif isinstance(src, dict):
            rv = dict()
            for key in src:
                rv[key.decode()] = cls.decode_redis(src[key])
            return rv
        elif isinstance(src, bytes):
            return json.loads(src.decode())
        else:
            raise Exception("type not handled: " + type(src))

    def __init__(self, index: str, redis: Redis) -> None:
        self.index = index
        self.redis = redis
        self.logger = logging.getLogger("CacheAPI:")

    async def get_scalar(self, key: str) -> Optional[BaseModel]:
        entry = f'{self.index}__{key}'
        object = await self.redis.get(f'{entry}')
        if object:
            self.logger.debug(f'Redis state key found: {entry}')
            return self.decode_redis(object)
        return None

    async def put_scalar(self, key: str, value: BaseModel) -> None:
        entry = f'{self.index}__{key}'
        self.logger.debug(f'Redis state put key: {entry}')
        await self.redis.set(entry, value.json())

    async def get_vector(self, key: str) -> list[Optional[dict]]:
        result = await self.get_scalar(key)
        return CacheIndex(**result).values if result else None

    async def put_vector(self, key: str, data: list[dict]) -> int:
        await self.put_scalar(key, CacheIndex(values=data))

    async def drop_key(self, key: str) -> int:
        await self.redis.delete(key)
