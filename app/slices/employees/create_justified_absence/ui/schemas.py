from pydantic import BaseModel
from uuid import UUID
from datetime import date


class CreateJustifiedAbsenceRequest(BaseModel):
    employee_id: UUID
    absence_date: date
    reason: str | None = None
