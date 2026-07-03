from decimal import Decimal
from uuid import UUID
from datetime import date
from typing import Optional
from app.shared.db.enums import LoanStatus
from app.shared.db.models import Loan
from app.slices.partner_loan.update_loan.infra.repository import UpdateLoanRepository
from app.slices.partner_loan.create_loan.domain.rules import validate_amount_dates

class UpdateLoan:
    def __init__(self, repository: UpdateLoanRepository):
        self.repository = repository

    async def execute(
        self,
        loan_id: UUID,
        principal_amount: Optional[Decimal] = None,
        interest_rate: Optional[Decimal] = None,
        total_amount: Optional[Decimal] = None,
        installments: Optional[int] = None,
        due_day: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[LoanStatus] = None,
    ) -> Loan:
        loan = await self.repository.get(loan_id)
        if not loan:
            raise ValueError("Loan not found")

        # Merge fields
        p_amount = principal_amount if principal_amount is not None else loan.principal_amount
        i_rate = interest_rate if interest_rate is not None else loan.interest_rate
        t_amount = total_amount if total_amount is not None else loan.total_amount
        inst = installments if installments is not None else loan.installments_qty
        d_day = due_day if due_day is not None else loan.due_day
        s_date = start_date if start_date is not None else loan.start_date
        e_date = end_date if end_date is not None else loan.end_date
        st = status if status is not None else loan.status

        # Validate merged fields
        validate_amount_dates(
            due_day=d_day,
            end_date=e_date,
            installments=inst,
            interest_rate=i_rate,
            principal_amount=p_amount,
            start_date=s_date,
            total_amount=t_amount,
        )

        # Apply updates
        loan.principal_amount = p_amount
        loan.interest_rate = i_rate
        loan.total_amount = t_amount
        loan.installments_qty = inst
        loan.due_day = d_day
        loan.start_date = s_date
        loan.end_date = e_date
        loan.status = st

        await self.repository.save(loan)
        return loan
