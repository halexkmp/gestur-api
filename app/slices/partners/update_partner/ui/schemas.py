from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.shared.db.enums import PartnerType


class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    pix_key: Optional[str] = None

class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    pix_key: Optional[str]
    type: PartnerType
    created_at: datetime

    class Config:
        from_attributes = True
