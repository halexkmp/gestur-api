from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import date
from app.shared.db.enums import PaymentMethod, PartnerCustomerShift

class SaleItemCreate(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float

class SalePaymentCreate(BaseModel):
    payment_method: PaymentMethod
    amount: float

class SaleCreate(BaseModel):
    partner_id: Optional[UUID] = None
    items: List[SaleItemCreate]
    payments: List[SalePaymentCreate]
    notes: Optional[str] = None
    observations: Optional[str] = None
    partner_customer_date: Optional[date] = None
    partner_customer_shift: Optional[PartnerCustomerShift] = None
