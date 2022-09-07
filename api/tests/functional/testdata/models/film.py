from uuid import UUID

from testdata.models.model import BaseOrJsonModel


class Film(BaseOrJsonModel):
    """Модель фильма."""
    id: UUID
    type: str
    title: str
    description: str
    imdb_rating: float
    genre: list[str]
    actors: list[dict]
    writers: list[dict]
    directors: list[dict]
