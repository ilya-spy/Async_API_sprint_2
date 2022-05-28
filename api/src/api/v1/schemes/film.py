from uuid import UUID

from pydantic import BaseModel

from api.v1.schemes.genre import Genre
from api.v1.schemes.person import PersonBase


class FilmBase(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genre: list[Genre]
    actors: list[PersonBase]
    writers: list[PersonBase]
    directors: list[PersonBase]
