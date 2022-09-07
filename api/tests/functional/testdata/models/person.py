from uuid import UUID

from testdata.models.model import BaseOrJsonModel


class Person(BaseOrJsonModel):
    """Модель персоны."""
    id: UUID
    full_name: str
    films: list[dict]
