from uuid import UUID

from pydantic import BaseModel


class PersonBase(BaseModel):
    uuid: UUID
    full_name: str


class PersonFilm(BaseModel):
    film_uuid: UUID
    role: str
    title: str


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilm]
