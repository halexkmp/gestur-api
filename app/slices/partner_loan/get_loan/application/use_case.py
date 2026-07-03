from uuid import UUID
from app.slices.partner_loan.get_loan.infra.repository import GetLoanRepository

class GetLoan:
    def __init__(self, repository: GetLoanRepository):
        self.repository = repository

    async def execute(self, loan_id: UUID):
        loan = await self.repository.get(loan_id)
        if not loan:
            raise ValueError("Loan not found")
        return loan
