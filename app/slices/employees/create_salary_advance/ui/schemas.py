from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


class CreateSalaryAdvanceRequest(BaseModel):
    employee_id: UUID
    amount: Decimal = Field(gt=0)
    advance_date: date
    note: str | None = None
    times: int = Field(gt=0)
