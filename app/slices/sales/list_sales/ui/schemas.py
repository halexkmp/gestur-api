from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from app.shared.db.enums import PaymentMethod, SaleStatus, PartnerCustomerShift

class SaleItemBase(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float

class SaleItemResponse(SaleItemBase):
    id: UUID
    total_price: float

    class Config:
        from_attributes = True

class SalePaymentBase(BaseModel):
    payment_method: PaymentMethod
    amount: float

class SalePaymentResponse(SalePaymentBase):
    id: UUID

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: UUID
    sale_code: str
    total_amount: float
    partner_id: Optional[UUID]
    user_id: UUID
    status: SaleStatus
    notes: Optional[str]
    observations: Optional[str]
    created_at: datetime
    items: List[SaleItemResponse]
    payments: List[SalePaymentResponse]

    class Config:
        from_attributes = True
