from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from aioredis import Redis


@dataclass
class BaseStorage(metaclass=ABCMeta):
    """Базовый класс для храненеия состояний etl."""

    @abstractmethod
    async def retrieve_state(self) -> dict:
        """Возвращает сохраненное состояние.

        :return:
        """
        pass

    @abstractmethod
    async def save_state(self, state: dict) -> bool:
        """Сохраняет состояние.

        :param state:
        :return:
        """
        pass


@dataclass
class RedisStorage(BaseStorage):
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


@dataclass
class State:
    """Управляет состоянием."""

    storage: BaseStorage
    _state: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._state = await self.storage.retrieve_state()

    async def retrieve_state(self, key: str) -> Any:
        """Возвращает сохраненное состояние по ключу.

        :param key:
        :return:
        """
        return self._state.get(key)

    async def save_state(self, key: str, value: Any):
        """Сохраняет значение по ключу.

        :param key:
        :param value:
        :return:
        """
        self._state[key] = value
        await self.storage.save_state(self._state)
