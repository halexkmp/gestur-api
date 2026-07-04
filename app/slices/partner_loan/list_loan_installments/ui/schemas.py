from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


class LoanInstallmentResponse(BaseModel):
    id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    payment_date: Optional[date] = None
    paid: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


