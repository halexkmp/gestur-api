from uuid import UUID
from app.shared.db.models import LoanInstallment

class ListLoanInstallmentsRepository:
    async def get_by_loan(self, loan_id: UUID) -> list[LoanInstallment]:
        return await LoanInstallment.filter(loan_id=loan_id).order_by("installment_number")
