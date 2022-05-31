from documents.film import Film as FilmDocument
from documents.genre import Genre as GenreDocument
from documents.person import Person as PersonDocument
from entities.film import Film as FilmEntity
from entities.person import Person as PersonEntity
from entities.person import RoleEnum
from message import Message

from transformers.base import BaseTransformer


class FilmTransformer(BaseTransformer):

    async def transform(self, messages: list[Message]) -> list[Message]:
        """Преобразует список моделей бд в список документов elasticsearch.

        :param messages:
        :return:
        """
        return [self.map(m) for m in messages]

    def map(self, message: Message) -> Message:
        """Преобразует модель бд в документ elasticsearch.

        :param message:
        :rtype: Message
        """
        item = FilmEntity(**message.obj_model.dict())
        message.obj_model = FilmDocument(
            id=item.id,
            type=item.type,
            imdb_rating=item.rating,
            title=item.title,
            description=item.description,
            genre=[GenreDocument(**g.dict()) for g in item.genres],
            directors=self.get_person(item.persons, RoleEnum.director),
            actors=self.get_person(item.persons, RoleEnum.actor),
            writers=self.get_person(item.persons, RoleEnum.writer),
        )
        return message

    @staticmethod
    def get_person(persons: list[PersonEntity], role: RoleEnum) -> list[PersonDocument]:
        """Фильтрует список персон по роли и возвращает список документов для elasticsearch.

        :param persons:
        :param role:
        :return:
        """
        return [PersonDocument(id=p.id, full_name=p.full_name, films=[])
                for p in persons if p.role == role]
