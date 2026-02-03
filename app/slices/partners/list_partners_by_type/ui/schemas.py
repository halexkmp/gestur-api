from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.shared.db.enums import PartnerType

class SaleResponse(BaseModel):
    id: UUID
    total_amount: float
    created_at: datetime

class PartnerResponse(BaseModel):
    id: UUID
    name: str
    active: bool
    pix_key: Optional[str] = None
    type: PartnerType
    sales: Optional[List[SaleResponse]] = None
    created_at: datetime

    class Config:
        from_attributes = True
