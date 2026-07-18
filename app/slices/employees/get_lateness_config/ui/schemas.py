from datetime import time
from decimal import Decimal

from pydantic import BaseModel


class LatenessConfigResponse(BaseModel):
    enabled: bool
    expected_entrance_time: time
    tolerance_minutes: int
    deduction_interval_minutes: int
    deduction_value: Decimal

    class Config:
        from_attributes = True
