from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import Optional
from app.shared.db.enums import LoanStatus

class LoanUpdateRequest(BaseModel):
    principal_amount: Optional[Decimal] = Field(None, gt=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0)
    installments_qty: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[LoanStatus] = None
