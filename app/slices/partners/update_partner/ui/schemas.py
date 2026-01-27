from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    pix_key: Optional[str] = None

class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    pix_key: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
