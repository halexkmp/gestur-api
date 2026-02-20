from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class CreateSalaryAdvanceRequest(BaseModel):
    employee_id: UUID
    amount: Decimal = Field(gt=0)
    note: str | None = None


class SalaryAdvanceResponse(BaseModel):
    id: UUID
    employee_id: UUID
    amount: Decimal
    created_at: datetime
    note: str | None

    class Config:
        from_attributes = True
