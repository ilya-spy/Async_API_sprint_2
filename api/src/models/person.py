from typing import Optional
from uuid import UUID

from utils.model_json import BaseOrJsonModel


class PersonFilm(BaseOrJsonModel):
    film_id: UUID
    role: str
    title: str


class Person(BaseOrJsonModel):
    """Модель персоны."""
    id: UUID
    full_name: str
    films: Optional[list[PersonFilm]]
