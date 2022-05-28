from typing import Optional
from uuid import UUID

from pydantic import BaseModel

import helpers


class PersonFilm(BaseModel):
    film_id: UUID
    role: str
    title: str

    class Config:
        json_loads = helpers.json_loads
        json_dumps = helpers.json_dumps


class Person(BaseModel):
    """Модель персоны."""
    id: UUID
    full_name: str
    films: Optional[list[PersonFilm]]

    class Config:
        json_loads = helpers.json_loads
        json_dumps = helpers.json_dumps
