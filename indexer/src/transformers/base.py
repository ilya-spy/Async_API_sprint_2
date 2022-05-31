from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from message import Message


@dataclass
class BaseTransformer(metaclass=ABCMeta):
    """Базовый класс для преобразователей."""

    @abstractmethod
    async def transform(self, messages: list[Message]) -> list[Message]:
        """Абстрактный метод преобразования сообщений.

        :param messages:
        :return:
        """
        pass
