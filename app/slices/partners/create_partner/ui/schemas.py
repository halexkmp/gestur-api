from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PartnerCreate(BaseModel):
    name: str
    active: bool = True

class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
