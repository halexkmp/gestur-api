from typing import Optional
from uuid import UUID
from app.shared.db.models import Loan

class UpdateLoanRepository:
    async def get(self, loan_id: UUID) -> Optional[Loan]:
        return await Loan.get_or_none(id=loan_id)

    async def save(self, loan: Loan) -> Loan:
        await loan.save()
        return loan
