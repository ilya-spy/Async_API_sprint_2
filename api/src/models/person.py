from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from models import helpers


class PersonFilm(BaseModel):
    film_id: UUID
    role: str


class Person(BaseModel):
    """Модель персоны."""
    id: UUID
    full_name: str
    films: Optional[List[PersonFilm]]

    class Config:
        json_loads = helpers.json_loads
        json_dumps = helpers.json_dumps
