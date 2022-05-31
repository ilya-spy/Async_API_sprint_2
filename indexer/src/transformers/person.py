from documents.person import Person as PersonDocument
from documents.person import PersonFilm as PersonFilmDocument
from entities.person import Person as PersonEntity
from entities.person import PersonFilm as PersonFilmEntity
from message import Message
from transformers.base import BaseTransformer


class PersonTransformer(BaseTransformer):

    async def transform(self, messages: list[Message]) -> list[Message]:
        """Преобразует модели персон из бд в список персон elasticsearch.

        :param messages:
        :return:
        """
        return [self.map(m) for m in messages]

    def map(self, message: Message) -> Message:
        """Преобразует модель бд в документ elasticsearch.

        :param message:
        :rtype: Message
        """
        item = PersonEntity(**message.obj_model.dict())
        message.obj_model = PersonDocument(
            id=item.id,
            full_name=item.full_name,
            films=[self.map_film(f) for f in item.films]
        )
        return message

    @staticmethod
    def map_film(item: PersonFilmEntity) -> PersonFilmDocument:
        return PersonFilmDocument(
            film_id=item.film_id,
            role=item.role,
            title=item.title,
        )
