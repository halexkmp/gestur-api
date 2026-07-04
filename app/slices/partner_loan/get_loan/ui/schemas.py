from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from app.shared.db.enums import LoanStatus


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


class LoanResponse(BaseModel):
    id: UUID
    start_date: date
    end_date: date
    interest_rate: Decimal
    status: LoanStatus
    principal_amount: Decimal
    total_amount: Decimal
    installments_qty: int
    installments: list[LoanInstallmentResponse]