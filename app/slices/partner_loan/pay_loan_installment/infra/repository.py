from typing import Optional
from uuid import UUID
from app.shared.db.models import LoanInstallment

class PayLoanInstallmentRepository:
    async def get(self, installment_id: UUID) -> Optional[LoanInstallment]:
        return await LoanInstallment.get_or_none(id=installment_id)

    async def save(self, installment: LoanInstallment) -> LoanInstallment:
        await installment.save()
        return installment
