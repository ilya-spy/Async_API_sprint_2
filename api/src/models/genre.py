from uuid import UUID

from models import base


class Genre(base.BaseOrJsonModel):
    """Модель жанра."""
    id: UUID
    name: str
