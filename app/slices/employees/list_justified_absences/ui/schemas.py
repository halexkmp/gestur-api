from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class JustifiedAbsenceItem(BaseModel):
    id: UUID
    employee_id: UUID
    absence_date: date
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True
