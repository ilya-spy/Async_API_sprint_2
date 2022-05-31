from uuid import UUID

from models import genre, person
from utils.model_json import BaseOrJsonModel


class Film(BaseOrJsonModel):
    """Модель фильма."""
    id: UUID
    type: str
    title: str
    description: str
    imdb_rating: float
    genre: list[genre.Genre]
    actors: list[person.Person]
    writers: list[person.Person]
    directors: list[person.Person]
