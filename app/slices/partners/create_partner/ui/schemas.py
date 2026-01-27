from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class PartnerCreate(BaseModel):
    name: str
    active: bool = True
    pix_key: Optional[str] = None

class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    pix_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
