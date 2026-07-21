from pydantic import BaseModel
from uuid import UUID


class EmployeeScheduleResponse(BaseModel):
    employee_id: UUID
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool

    class Config:
        from_attributes = True
