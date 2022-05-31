from documents.genre import Genre as GenreDocument
from entities.genre import Genre as GenreEntity
from message import Message

from transformers.base import BaseTransformer


class GenreTransformer(BaseTransformer):

    async def transform(self, messages: list[Message]) -> list[Message]:
        """Преобразует модели жанров из бд в список жанров elasticsearch.

        :param messages:
        :return:
        """
        return [self.map(m) for m in messages]

    @staticmethod
    def map(message: Message) -> Message:
        """Преобразует модель бд в документ elasticsearch.

        :param message:
        :rtype: Message
        """
        item = GenreEntity(**message.obj_model.dict())
        message.obj_model = GenreDocument(
            id=item.id,
            name=item.name
        )
        return message
