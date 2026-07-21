from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import List, Literal


class AttendanceDayItem(BaseModel):
    date: date
    status: Literal["PRESENT", "JUSTIFIED_ABSENCE", "UNJUSTIFIED_ABSENCE"]


class EmployeeScheduleOverviewItem(BaseModel):
    employee_id: UUID
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool
    month: int
    year: int
    days: List[AttendanceDayItem]
    unjustified_absence_count: int


class EmployeeScheduleOverviewResponse(BaseModel):
    items: List[EmployeeScheduleOverviewItem]
