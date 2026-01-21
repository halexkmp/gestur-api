from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from app.layers.db.enums import PaymentMethod, SaleStatus, PartnerCustomerShift

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

class SaleCreate(BaseModel):
    bugueiro_id: Optional[UUID] = None
    partner_id: Optional[UUID] = None
    notes: Optional[str] = None
    observations: Optional[str] = None
    items: List[SaleItemBase]
    payments: List[SalePaymentBase]
    # For bugueiro client if applicable
    bugueiro_client_date: Optional[date] = None
    bugueiro_client_shift: Optional[PartnerCustomerShift] = None

class SaleResponse(BaseModel):
    id: UUID
    sale_number: int
    total_amount: float
    bugueiro_id: Optional[UUID]
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
