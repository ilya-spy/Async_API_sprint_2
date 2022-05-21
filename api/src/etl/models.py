from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Message(BaseModel):
    producer_name: str
    obj_id: UUID
    obj_modified: datetime
    obj_model: Optional[BaseModel]


class RoleEnum(str, Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'


class PersonFilm(BaseModel):
    id: UUID
    role: str


class Person(BaseModel):
    id: UUID
    full_name: str
    role: Optional[RoleEnum]
    films: Optional[list[PersonFilm]]


class Genre(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    type: str
    title: str
    description: str
    rating: float
    genres: list[Genre]
    persons: list[Person]
