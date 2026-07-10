from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from app.shared.db.enums import LoanStatus, LoanInstallmentStatus

class PaymentSummaryResponse(BaseModel):
    id: UUID
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class InstallmentSummaryResponse(BaseModel):
    id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    status: LoanInstallmentStatus
    payment_date: Optional[date] = None
    payments: List[PaymentSummaryResponse]

    class Config:
        from_attributes = True

class LoanSummaryResponse(BaseModel):
    id: UUID
    partner_id: UUID
    partner_name: str
    principal_amount: Decimal
    interest_rate: Decimal
    total_amount: Decimal
    installments_qty: int
    due_weekday: str
    start_date: date
    end_date: date
    status: LoanStatus
    created_at: datetime
    total_paid: Decimal
    remaining_balance: Decimal
    total_payments: int
    paid_installments: int
    partially_paid_installments: int
    pending_installments: int
    installments: List[InstallmentSummaryResponse]

    class Config:
        from_attributes = True
