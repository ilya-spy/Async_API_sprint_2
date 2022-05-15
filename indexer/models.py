from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(str, Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'


class Person(BaseModel):
    id: UUID
    role: RoleEnum
    full_name: str


class Movie(BaseModel):
    id: UUID
    title: str
    description: str
    rating: float
    genres: list[str]
    persons: list[Person]
