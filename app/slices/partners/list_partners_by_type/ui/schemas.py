from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.shared.db.enums import PartnerType


class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    pix_key: Optional[str] = None
    type: PartnerType
    created_at: datetime

    class Config:
        from_attributes = True
