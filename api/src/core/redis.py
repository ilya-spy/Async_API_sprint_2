import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from aioredis import Redis
from pydantic import BaseModel

from core.interfaces import CacheAPI, CacheIndex


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
            return src.decode()
        else:
            raise Exception("type not handled: " + type(src))

    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.logger = logging.getLogger("CacheAPI:")

    async def get_scalar(self, key: str) -> Optional[BaseModel]:
        object = await self.redis.hgetall(key)
        if object:
            self.logger.debug(f'Redis state key found: {key}')
            return self.decode_redis(object)
        return None

    async def put_scalar(self, key: str, value: BaseModel) -> None:
        self.logger.debug(f'Redis state put key: {key}')
        await self.redis.hmset(key, dict(value))

    async def get_vector(self, key: str) -> list[Optional[dict]]:
        result = await self.get_scalar(key)
        return CacheIndex(**result).values if result else None

    async def put_vector(self, key: str, data: list[dict]) -> int:
        await self.put_scalar(key, CacheIndex(values=data))

    async def drop_key(self, key: str) -> int:
        await self.redis.delete(key)
