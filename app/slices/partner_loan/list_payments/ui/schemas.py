from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

class PaymentResponse(BaseModel):
    id: UUID
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
