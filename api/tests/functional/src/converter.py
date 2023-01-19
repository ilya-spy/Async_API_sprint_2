from pydantic import BaseModel

from testdata.models.model import BaseOrJsonModel

from testdata.models.genre import Genre as GenreModel
from testdata.schemes.v1.genre import Genre

from testdata.models.person import Person as PersonModel
from testdata.schemes.v1.person import Person, PersonFilm


class BaseConverter:
    @staticmethod
    def convert(model: BaseModel) -> BaseOrJsonModel:
        pass


class GenreConverter(BaseConverter):
    @staticmethod
    def convert(model: GenreModel) -> Genre:
        return Genre(
            uuid=model['id'],
            name=model['name']
        ).dict()


class PersonConverter(BaseConverter):
    @staticmethod
    def convert(model: PersonModel) -> Person:
        return Person(
            uuid=model['id'],
            full_name=model['full_name'],
            films=[PersonFilm(film_uuid=film['film_id'], role=film['role'], title=film['title'])
                   for film in model['films']]
        ).dict()
