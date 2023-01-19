from uuid import UUID

from testdata.schemes.v1.genre import Genre
from testdata.schemes.v1.person import PersonBase
from testdata.models.model import BaseOrJsonModel


class FilmBase(BaseOrJsonModel):
    uuid: UUID
    title: str
    imdb_rating: float


class Film(BaseOrJsonModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genre: list[Genre]
    actors: list[PersonBase]
    writers: list[PersonBase]
    directors: list[PersonBase]
