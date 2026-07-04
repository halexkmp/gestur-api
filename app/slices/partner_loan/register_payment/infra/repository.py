from typing import Optional
from uuid import UUID
from app.shared.db.models import LoanInstallment, LoanInstallmentPayment

class RegisterPaymentRepository:
    async def get_installment(self, installment_id: UUID) -> Optional[LoanInstallment]:
        return await LoanInstallment.get_or_none(id=installment_id).prefetch_related("payments")

    async def save_payment(self, payment: LoanInstallmentPayment) -> LoanInstallmentPayment:
        await payment.save()
        return payment

    async def save_installment(self, installment: LoanInstallment) -> LoanInstallment:
        await installment.save()
        return installment
