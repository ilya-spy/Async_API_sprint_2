import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

from aioredis import Redis
from pydantic import BaseModel


@dataclass
class RedisStorage:
    """Обеспечивает хранение состояния в redis."""
    redis: Redis
    name: str

    async def retrieve_state(self) -> Any:
        """Возвращает сохраненное состояние.

        :return:
        """
        state = await self.redis.hgetall(self.name)
        return self.decode_redis(state)

    async def save_state(self, state: dict) -> None:
        """
        Сохраняет состояние.

        :param state:
        :return:
        """
        await self.redis.hset(self.name, mapping=state)

    @classmethod
    def decode_redis(cls, src):
        """Преобразует поля из бинарного формата в формат python

        :param src:
        :return:
        """
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


class CacheIndex(BaseModel):
    values: list[dict]


class CacheAPI:
    def __init__(self, index: str, redis: Redis) -> None:
        self.index = index
        self.redis = redis
        self.logger = logging.getLogger("CacheAPI: " + index)
        self.storage = RedisStorage(self.redis, name=self.index)

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
