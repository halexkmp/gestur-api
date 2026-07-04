from uuid import UUID
from app.shared.db.models import Loan
from app.slices.partner_loan.list_loan_installments.infra.repository import ListLoanInstallmentsRepository

class ListLoanInstallments:
    def __init__(self, repository: ListLoanInstallmentsRepository):
        self.repository = repository

    async def execute(self, loan_id: UUID):
        loan = await Loan.get_or_none(id=loan_id)
        if not loan:
            raise ValueError("Loan not found")
        return await self.repository.get_by_loan(loan_id)
