from uuid import UUID

from models import base, genre, person


class Film(base.BaseOrJsonModel):
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
