from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Dict, List
from uuid import UUID

from app.slices.partner_loan.period_summary.domain.rules import (
    installment_profit_share,
    received_for_installment,
    validate_date_range,
)
from app.slices.partner_loan.period_summary.infra.repository import PeriodSummaryRepository


@dataclass
class PartnerPeriodEntryDTO:
    partner_id: UUID
    partner_name: str
    scheduled_amount: Decimal
    received_amount: Decimal
    outstanding_amount: Decimal
    installments_count: int


@dataclass
class LoanPeriodSummaryDTO:
    start_date: date
    end_date: date
    expected_revenue: Decimal
    expected_capital: Decimal
    expected_profit: Decimal
    received_amount: Decimal
    outstanding_amount: Decimal
    installments_count: int
    partners_count: int
    partners: List[PartnerPeriodEntryDTO]


class PeriodSummary:
    def __init__(self, repository: PeriodSummaryRepository):
        self.repository = repository

    async def execute(self, start_date: date, end_date: date) -> LoanPeriodSummaryDTO:
        validate_date_range(start_date, end_date)

        installments = await self.repository.list_installments_in_range(start_date, end_date)

        # Seeded at "0.00", never "0": Decimal carries its scale through
        # serialization, so a bare-zero seed would render an empty range as 0.
        expected_revenue = Decimal("0.00")
        received_amount = Decimal("0.00")
        raw_profit = Decimal("0.00")
        entries: Dict[UUID, PartnerPeriodEntryDTO] = {}

        for installment in installments:
            loan = installment.loan
            partner = loan.partner

            installment_received = received_for_installment(
                [payment.amount for payment in installment.payments],
                installment.amount,
            )

            expected_revenue += installment.amount
            received_amount += installment_received
            raw_profit += installment_profit_share(
                installment.amount, loan.principal_amount, loan.total_amount
            )

            entry = entries.get(partner.id)
            if entry is None:
                entry = PartnerPeriodEntryDTO(
                    partner_id=partner.id,
                    partner_name=partner.name,
                    scheduled_amount=Decimal("0.00"),
                    received_amount=Decimal("0.00"),
                    outstanding_amount=Decimal("0.00"),
                    installments_count=0,
                )
                entries[partner.id] = entry

            entry.scheduled_amount += installment.amount
            entry.received_amount += installment_received
            entry.installments_count += 1

        # Profit is the only value that needs rounding: its per-installment
        # shares are full-precision ratios. Everything else is derived by
        # subtraction from two 2dp operands, which keeps the totals exact.
        expected_profit = raw_profit.quantize(Decimal("0.01"))
        expected_capital = expected_revenue - expected_profit
        outstanding_amount = expected_revenue - received_amount

        for entry in entries.values():
            entry.outstanding_amount = entry.scheduled_amount - entry.received_amount

        partners = sorted(
            entries.values(),
            key=lambda entry: (-entry.scheduled_amount, entry.partner_name),
        )

        return LoanPeriodSummaryDTO(
            start_date=start_date,
            end_date=end_date,
            expected_revenue=expected_revenue,
            expected_capital=expected_capital,
            expected_profit=expected_profit,
            received_amount=received_amount,
            outstanding_amount=outstanding_amount,
            installments_count=len(installments),
            partners_count=len(partners),
            partners=partners,
        )
