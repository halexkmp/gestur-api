from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import List


class PartnerPeriodEntryResponse(BaseModel):
    partner_id: UUID
    partner_name: str
    scheduled_amount: Decimal
    received_amount: Decimal
    outstanding_amount: Decimal
    installments_count: int

    class Config:
        from_attributes = True


class LoanPeriodSummaryResponse(BaseModel):
    start_date: date
    end_date: date
    expected_revenue: Decimal
    expected_capital: Decimal
    expected_profit: Decimal
    received_amount: Decimal
    outstanding_amount: Decimal
    installments_count: int
    partners_count: int
    partners: List[PartnerPeriodEntryResponse]

    class Config:
        from_attributes = True
