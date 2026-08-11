from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal


from app.shared.db.enums import LoanInstallmentStatus


class UpcomingInstallmentResponse(BaseModel):
    installment_id: UUID
    loan_id: UUID
    partner_id: UUID
    partner_name: str
    installment_number: int
    due_date: date
    amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: LoanInstallmentStatus
    is_overdue: bool

    class Config:
        from_attributes = True
