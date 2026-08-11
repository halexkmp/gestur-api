from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.shared.db.enums import LoanInstallmentStatus
from app.slices.partner_loan.upcoming_installments.domain.rules import (
    is_overdue_on,
    received_for_installment,
    resolve_lower_bound,
    validate_date_range,
)
from app.slices.partner_loan.upcoming_installments.infra.repository import (
    UpcomingInstallmentsRepository,
)


@dataclass
class UpcomingInstallmentDTO:
    installment_id: UUID
    loan_id: UUID
    partner_id: UUID
    partner_name: str
    installment_number: int
    due_date: date
    amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: LoanInstallmentStatus
    is_overdue: bool


class ListUpcomingInstallments:
    def __init__(self, repository: UpcomingInstallmentsRepository):
        self.repository = repository

    async def execute(
        self,
        start_date: date,
        end_date: date,
        include_overdue: bool = False,
        partner_id: Optional[UUID] = None,
        limit: Optional[int] = None,
    ) -> List[UpcomingInstallmentDTO]:
        # start_date stays required and the reversed-range check still applies
        # even when include_overdue turns it into a non-bound.
        validate_date_range(start_date, end_date)

        installments = await self.repository.list_due_installments(
            resolve_lower_bound(start_date, include_overdue),
            end_date,
            partner_id,
            limit,
        )

        # Resolved once, before the loop: every row in one response must be
        # judged overdue against the same date, even across a midnight rollover.
        reference_date = date.today()

        rows: List[UpcomingInstallmentDTO] = []
        for installment in installments:
            loan = installment.loan
            partner = loan.partner

            paid_amount = received_for_installment(
                [payment.amount for payment in installment.payments],
                installment.amount,
            )

            rows.append(
                UpcomingInstallmentDTO(
                    installment_id=installment.id,
                    loan_id=loan.id,
                    partner_id=partner.id,
                    partner_name=partner.name,
                    installment_number=installment.installment_number,
                    due_date=installment.due_date,
                    amount=installment.amount,
                    paid_amount=paid_amount,
                    remaining_amount=installment.amount - paid_amount,
                    status=installment.status,
                    is_overdue=is_overdue_on(installment.due_date, reference_date),
                )
            )

        return rows
