from uuid import UUID

from pydantic import BaseModel


class PersonBase(BaseModel):
    uuid: UUID
    full_name: str


class Person(BaseModel):
    uuid: UUID
    full_name: str
    role: str
    film_ids: list[UUID]
