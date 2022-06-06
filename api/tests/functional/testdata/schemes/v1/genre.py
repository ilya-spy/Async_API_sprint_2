from uuid import UUID

from testdata.models.model_json import BaseOrJsonModel


class Genre(BaseOrJsonModel):
    uuid: UUID
    name: str
