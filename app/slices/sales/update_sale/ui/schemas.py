from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from app.shared.db.enums import PaymentMethod, SaleStatus


class SaleItemUpdate(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float


class SalePaymentUpdate(BaseModel):
    payment_method: PaymentMethod
    amount: float


class SaleUpdate(BaseModel):
    partner_id: Optional[UUID] = None
    status: Optional[SaleStatus] = None
    notes: Optional[str] = None
    observations: Optional[str] = None
    items: Optional[List[SaleItemUpdate]] = None
    payments: Optional[List[SalePaymentUpdate]] = None
    modified_by: Optional[str] = None
