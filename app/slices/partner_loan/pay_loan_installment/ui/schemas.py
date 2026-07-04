from pydantic import BaseModel
from datetime import date
from typing import Optional

class PayInstallmentRequest(BaseModel):
    payment_date: Optional[date] = None
