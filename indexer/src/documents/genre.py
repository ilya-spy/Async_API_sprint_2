from uuid import UUID

import helpers
from pydantic import BaseModel


class Genre(BaseModel):
    """Модель жанра."""
    id: UUID
    name: str

    class Config:
        json_loads = helpers.json_loads
        json_dumps = helpers.json_dumps
