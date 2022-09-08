from uuid import UUID

from testdata.models.model import BaseOrJsonModel


class Genre(BaseOrJsonModel):
    """Модель жанра."""
    id: UUID
    name: str
