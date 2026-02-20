from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


class SalaryAdvanceItem(BaseModel):
    id: UUID
    amount: Decimal
    employee_id: UUID
    created_at: datetime
    note: Optional[str] = None

    class Config:
        from_attributes = True
