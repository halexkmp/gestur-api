from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


class SalarySummaryResponse(BaseModel):
    employee_id: UUID
    month: int
    year: int
    gross_salary: Decimal
    advances_total: Decimal
    late_delay_minutes: int
    late_days_count: int
    late_deduction_total: Decimal
    net_salary: Decimal

    class Config:
        from_attributes = True
