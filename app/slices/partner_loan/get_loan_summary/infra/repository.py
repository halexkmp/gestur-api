from typing import Optional
from uuid import UUID
from app.shared.db.models import Loan

class GetLoanSummaryRepository:
    async def get_loan_with_details(self, loan_id: UUID) -> Optional[Loan]:
        return await Loan.get_or_none(id=loan_id).prefetch_related("partner", "installments__payments")
