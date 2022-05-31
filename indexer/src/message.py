from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Message(BaseModel):
    producer_name: str
    obj_id: UUID
    obj_modified: datetime
    obj_model: Optional[BaseModel]
