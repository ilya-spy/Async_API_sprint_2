from typing import Optional
from uuid import UUID

from models import base

class PersonFilm(base.BaseOrJsonModel):
    film_id: UUID
    role: str
    title: str


class Person(base.BaseOrJsonModel):
    """Модель персоны."""
    id: UUID
    full_name: str
    films: Optional[list[PersonFilm]]
