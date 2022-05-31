from uuid import UUID

from utils.model_json import BaseOrJsonModel


class PersonBase(BaseOrJsonModel):
    uuid: UUID
    full_name: str


class PersonFilm(BaseOrJsonModel):
    film_uuid: UUID
    role: str
    title: str


class Person(BaseOrJsonModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilm]
