from uuid import UUID

from utils.model_json import BaseOrJsonModel


class Genre(BaseOrJsonModel):
    uuid: UUID
    name: str
