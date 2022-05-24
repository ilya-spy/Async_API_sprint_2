from uuid import UUID

from pydantic import BaseModel

from models import helpers


class Genre(BaseModel):
    """Модель жанра."""
    id: UUID
    name: str

    class Config:
        json_loads = helpers.json_loads
        json_dumps = helpers.json_dumps
