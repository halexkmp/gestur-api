from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.shared.db.enums import SaleStatus, PaymentMethod


class SaleItemReport(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True


class SalePaymentReport(BaseModel):
    id: UUID
    payment_method: PaymentMethod
    amount: float

    class Config:
        from_attributes = True


class SaleReportResponse(BaseModel):
    id: UUID
    sale_code: str
    total_amount: float
    partner_id: Optional[UUID]
    user_id: UUID
    status: SaleStatus
    notes: Optional[str]
    observations: Optional[str]
    created_at: datetime
    items: List[SaleItemReport]
    payments: List[SalePaymentReport]

    class Config:
        from_attributes = True
