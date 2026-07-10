from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from app.shared.db.enums import LoanStatus, LoanInstallmentStatus
from app.slices.partner_loan.get_loan_summary.infra.repository import GetLoanSummaryRepository

@dataclass
class PaymentSummaryDTO:
    id: UUID
    amount: Decimal
    payment_date: date
    notes: Optional[str]

@dataclass
class InstallmentSummaryDTO:
    id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    status: LoanInstallmentStatus
    payment_date: Optional[date]
    payments: List[PaymentSummaryDTO]

@dataclass
class LoanSummaryDTO:
    id: UUID
    partner_id: UUID
    partner_name: str
    principal_amount: Decimal
    interest_rate: Decimal
    total_amount: Decimal
    installments_qty: int
    due_weekday: str
    start_date: date
    end_date: date
    status: LoanStatus
    created_at: datetime
    total_paid: Decimal
    remaining_balance: Decimal
    total_payments: int
    paid_installments: int
    partially_paid_installments: int
    pending_installments: int
    installments: List[InstallmentSummaryDTO]

class GetLoanSummary:
    def __init__(self, repository: GetLoanSummaryRepository):
        self.repository = repository

    async def execute(self, loan_id: UUID) -> LoanSummaryDTO:
        loan = await self.repository.get_loan_with_details(loan_id)
        if not loan:
            raise ValueError("Loan not found")

        # Sort installments by installment_number ASC
        sorted_installments = sorted(loan.installments, key=lambda inst: inst.installment_number)

        installment_dtos = []
        total_paid = Decimal("0.00")
        total_payments_count = 0
        paid_installments_count = 0
        partially_paid_installments_count = 0
        pending_installments_count = 0

        for inst in sorted_installments:
            # Sort payments by payment_date ASC
            sorted_payments = sorted(inst.payments, key=lambda p: p.payment_date)
            
            payment_dtos = []
            for p in sorted_payments:
                payment_dtos.append(
                    PaymentSummaryDTO(
                        id=p.id,
                        amount=p.amount,
                        payment_date=p.payment_date,
                        notes=p.notes,
                    )
                )
                total_paid += p.amount
                total_payments_count += 1

            if inst.status == LoanInstallmentStatus.PAID:
                paid_installments_count += 1
            elif inst.status == LoanInstallmentStatus.PARTIALLY_PAID:
                partially_paid_installments_count += 1
            elif inst.status == LoanInstallmentStatus.PENDING:
                pending_installments_count += 1

            installment_dtos.append(
                InstallmentSummaryDTO(
                    id=inst.id,
                    installment_number=inst.installment_number,
                    amount=inst.amount,
                    due_date=inst.due_date,
                    status=inst.status,
                    payment_date=inst.payment_date,
                    payments=payment_dtos,
                )
            )

        due_weekday = loan.start_date.strftime("%A")
        remaining_balance = round(loan.total_amount - total_paid, 2)
        total_paid = round(total_paid, 2)

        return LoanSummaryDTO(
            id=loan.id,
            partner_id=loan.partner.id,
            partner_name=loan.partner.name,
            principal_amount=loan.principal_amount,
            interest_rate=loan.interest_rate,
            total_amount=loan.total_amount,
            installments_qty=loan.installments_qty,
            due_weekday=due_weekday,
            start_date=loan.start_date,
            end_date=loan.end_date,
            status=loan.status,
            created_at=loan.created_at,
            total_paid=total_paid,
            remaining_balance=remaining_balance,
            total_payments=total_payments_count,
            paid_installments=paid_installments_count,
            partially_paid_installments=partially_paid_installments_count,
            pending_installments=pending_installments_count,
            installments=installment_dtos,
        )
