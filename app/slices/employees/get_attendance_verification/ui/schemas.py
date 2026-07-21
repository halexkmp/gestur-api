from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import List, Literal


class AttendanceDayItem(BaseModel):
    date: date
    status: Literal["PRESENT", "JUSTIFIED_ABSENCE", "UNJUSTIFIED_ABSENCE"]


class AttendanceVerificationResponse(BaseModel):
    employee_id: UUID
    month: int
    year: int
    days: List[AttendanceDayItem]
    unjustified_absence_count: int
