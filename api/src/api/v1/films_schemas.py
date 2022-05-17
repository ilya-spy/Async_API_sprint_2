from uuid import UUID

from pydantic import BaseModel


class Genre(BaseModel):
    id: UUID
    name: str


class Person(BaseModel):
    id: UUID
    full_name: str


class FilmBase(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class FilmDetails(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
