from typing import Optional
from uuid import UUID

import helpers
from pydantic import BaseModel


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
