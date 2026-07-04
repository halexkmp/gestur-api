from uuid import UUID
from typing import List
from app.shared.db.models import LoanInstallmentPayment
from app.slices.partner_loan.list_payments.infra.repository import ListPaymentsRepository

class ListPayments:
    def __init__(self, repository: ListPaymentsRepository):
        self.repository = repository

    async def execute(self, installment_id: UUID) -> List[LoanInstallmentPayment]:
        exists = await self.repository.installment_exists(installment_id)
        if not exists:
            raise ValueError("Installment not found")

        return await self.repository.list_by_installment(installment_id)
