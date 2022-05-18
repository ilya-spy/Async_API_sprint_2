from uuid import UUID

from pydantic import BaseModel


class Person(BaseModel):
    id: UUID
    full_name: str


class Genre(BaseModel):
    id: UUID
    name: str


class Movie(BaseModel):
    id: UUID
    type: str
    title: str
    description: str
    imdb_rating: float
    genre: list[Genre]
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]
