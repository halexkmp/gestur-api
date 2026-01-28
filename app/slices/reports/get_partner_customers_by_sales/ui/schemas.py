from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from app.shared.db.enums import PartnerCustomerShift


class PartnerCustomerReport(BaseModel):
    id: UUID
    partner_id: Optional[UUID]
    sale_id: UUID
    quantity: int
    shift: PartnerCustomerShift

    class Config:
        from_attributes = True
