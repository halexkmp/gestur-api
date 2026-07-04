from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from app.shared.db.enums import LoanStatus

class LoanCreateRequest(BaseModel):
    partner_id: UUID
    principal_amount: Decimal = Field(gt=0)
    interest_rate: Decimal = Field(ge=0)
    installments_qty: int = Field(gt=0)
    start_date: date

class LoanResponse(BaseModel):
    id: UUID
    partner_id: UUID
    principal_amount: Decimal
    interest_rate: Decimal
    total_amount: Decimal
    installments_qty: int
    start_date: date
    end_date: date
    status: LoanStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
