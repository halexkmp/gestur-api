from datetime import date
from uuid import UUID
from typing import Optional
from app.shared.db.enums import LoanInstallmentStatus
from app.slices.partner_loan.pay_loan_installment.infra.repository import PayLoanInstallmentRepository

class PayLoanInstallment:
    def __init__(self, repository: PayLoanInstallmentRepository):
        self.repository = repository

    async def execute(self, installment_id: UUID, payment_date: Optional[date] = None):
        installment = await self.repository.get(installment_id)
        if not installment:
            raise ValueError("Installment not found")

        installment.status = LoanInstallmentStatus.PAID
        installment.payment_date = payment_date if payment_date is not None else date.today()

        await self.repository.save(installment)
        return installment
