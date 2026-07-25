from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import List, Optional


class SalaryAdvanceItem(BaseModel):
    id: UUID
    amount: Decimal
    advance_date: date
    note: Optional[str] = None

    class Config:
        from_attributes = True


class SalarySummaryItem(BaseModel):
    employee_id: UUID
    month: int
    year: int
    gross_salary: Decimal
    advances_total: Decimal
    advances: List[SalaryAdvanceItem]
    late_delay_minutes: int
    late_days_count: int
    late_deduction_total: Decimal
    net_salary: Decimal

    class Config:
        from_attributes = True


class SalarySummaryOverviewResponse(BaseModel):
    items: List[SalarySummaryItem]
