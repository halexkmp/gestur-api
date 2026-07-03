from app.shared.db.models import Loan

class ListLoansRepository:
    async def list_all(self) -> list[Loan]:
        return await Loan.all()
