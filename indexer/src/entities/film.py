from uuid import UUID

from pydantic import BaseModel

from entities.genre import Genre
from entities.person import Person


class Film(BaseModel):
    id: UUID
    type: str
    title: str
    description: str
    rating: float
    genres: list[Genre]
    persons: list[Person]
