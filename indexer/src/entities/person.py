from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(str, Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'


class PersonFilm(BaseModel):
    film_id: UUID
    role: RoleEnum
    title: str


class Person(BaseModel):
    id: UUID
    full_name: str
    role: Optional[RoleEnum]
    films: Optional[list[PersonFilm]]
