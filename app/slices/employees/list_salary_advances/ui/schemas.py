from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional, List


class SalaryAdvanceItem(BaseModel):
    id: UUID
    employee_id: UUID
    amount: Decimal
    paid_at: date
    note: Optional[str] = None

    class Config:
        from_attributes = True
