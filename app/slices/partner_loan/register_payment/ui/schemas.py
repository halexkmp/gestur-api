from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

class PaymentRegisterRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_date: date
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: UUID
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
