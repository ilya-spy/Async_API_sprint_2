from typing import List
from uuid import UUID

from pydantic import BaseModel

from models import genre, helpers, person


class Film(BaseModel):
    """Модель фильма."""
    id: UUID
    type: str
    title: str
    description: str
    imdb_rating: float
    genre: List[genre.Genre]
    actors: List[person.Person]
    writers: List[person.Person]
    directors: List[person.Person]

    class Config:
        json_loads = helpers.json_loads
        json_dumps = helpers.json_dumps
