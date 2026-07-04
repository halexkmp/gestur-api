from app.slices.partner_loan.list_loans.infra.repository import ListLoansRepository

class ListLoans:
    def __init__(self, repository: ListLoansRepository):
        self.repository = repository

    async def execute(self, partner_id: str):
        return await self.repository.list_by_partner(partner_id)
