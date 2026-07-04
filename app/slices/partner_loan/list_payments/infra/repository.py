from typing import List
from uuid import UUID
from app.shared.db.models import LoanInstallment, LoanInstallmentPayment

class ListPaymentsRepository:
    async def installment_exists(self, installment_id: UUID) -> bool:
        return await LoanInstallment.filter(id=installment_id).exists()

    async def list_by_installment(self, installment_id: UUID) -> List[LoanInstallmentPayment]:
        return await LoanInstallmentPayment.filter(loan_installment_id=installment_id).order_by("payment_date")
