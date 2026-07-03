from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.shared.db.enums import PartnerType


class PartnerCreate(BaseModel):
    name: str
    active: bool = True
    type: PartnerType
    pix_key: Optional[str] = None

class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    pix_key: Optional[str] = None
    type: PartnerType
    created_at: datetime

    class Config:
        from_attributes = True
