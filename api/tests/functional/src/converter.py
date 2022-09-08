from pydantic import BaseModel

from testdata.models.model import BaseOrJsonModel
from testdata.models.genre import Genre as GenreModel
from testdata.schemes.v1.genre import Genre


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
