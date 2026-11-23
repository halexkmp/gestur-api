from datetime import time
from decimal import Decimal

from pydantic import BaseModel


class UpdateLatenessConfigRequest(BaseModel):
    enabled: bool
    expected_entrance_time: time
    tolerance_minutes: int
    deduction_interval_minutes: int
    deduction_value: Decimal
    late_penalty_hours: Decimal
    monthly_work_hours: int


class LatenessConfigResponse(BaseModel):
    enabled: bool
    expected_entrance_time: time
    tolerance_minutes: int
    deduction_interval_minutes: int
    deduction_value: Decimal
    late_penalty_hours: Decimal
    monthly_work_hours: int

    class Config:
        from_attributes = True
