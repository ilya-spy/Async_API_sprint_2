from uuid import UUID

from models.base import BaseOrJsonModel


class Genre(BaseOrJsonModel):
    uuid: UUID
    name: str
