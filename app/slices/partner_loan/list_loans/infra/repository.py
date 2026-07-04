from app.shared.db.models import Loan

class ListLoansRepository:
    async def list_by_partner(self, partner_id:str) -> list[Loan]:
        return await Loan.filter(partner_id=partner_id)
