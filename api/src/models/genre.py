from uuid import UUID

from utils.model_json import BaseOrJsonModel


class Genre(BaseOrJsonModel):
    """Модель жанра."""
    id: UUID
    name: str
