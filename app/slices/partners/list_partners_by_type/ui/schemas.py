from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
