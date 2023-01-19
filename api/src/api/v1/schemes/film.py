from uuid import UUID

from api.v1.schemes.genre import Genre
from api.v1.schemes.person import PersonBase
from models.base import BaseOrJsonModel


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
