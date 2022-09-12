from uuid import UUID

from testdata.models.model import BaseOrJsonModel


class PersonFilm(BaseOrJsonModel):
    film_id: UUID
    role: str
    title: str


class Person(BaseOrJsonModel):
    """Модель персоны."""
    id: UUID
    full_name: str
    films: list[PersonFilm]
