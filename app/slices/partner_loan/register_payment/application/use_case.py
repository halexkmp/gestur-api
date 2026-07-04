from datetime import date
from decimal import Decimal
from uuid import UUID
from typing import Optional
from tortoise.transactions import in_transaction

from app.shared.db.enums import LoanInstallmentStatus
from app.shared.db.models import LoanInstallmentPayment, LoanInstallment
from app.slices.partner_loan.register_payment.infra.repository import RegisterPaymentRepository

class RegisterPayment:
    def __init__(self, repository: RegisterPaymentRepository):
        self.repository = repository

    async def execute(
        self,
        installment_id: UUID,
        amount: Decimal,
        payment_date: date,
        notes: Optional[str] = None,
    ) -> tuple[LoanInstallmentPayment, LoanInstallment]:
        # Load installment and payments
        installment = await self.repository.get_installment(installment_id)
        if not installment:
            raise ValueError("Installment not found")

        # Calculate remaining balance
        total_paid = Decimal("0")
        for p in installment.payments:
            total_paid += p.amount
        
        remaining_balance = installment.amount - total_paid

        # Validations
        if amount <= Decimal("0"):
            raise ValueError("Payment amount must be greater than zero")
        if amount > remaining_balance:
            raise ValueError("Payment amount cannot exceed the remaining balance")

        # Atomic database updates
        async with in_transaction():
            payment = LoanInstallmentPayment(
                loan_installment=installment,
                amount=amount,
                payment_date=payment_date,
                notes=notes,
            )
            saved_payment = await self.repository.save_payment(payment)

            new_total_paid = total_paid + amount
            if new_total_paid == installment.amount:
                installment.status = LoanInstallmentStatus.PAID
                installment.payment_date = payment_date
            else:
                installment.status = LoanInstallmentStatus.PARTIALLY_PAID
                installment.payment_date = None

            await self.repository.save_installment(installment)

        return saved_payment, installment
