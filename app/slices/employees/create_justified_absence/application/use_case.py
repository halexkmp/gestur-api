from uuid import UUID
from datetime import date
from typing import Optional

from app.shared.db.models import JustifiedAbsence
from app.slices.employees.create_justified_absence.infra.repository import CreateJustifiedAbsenceRepository

WEEKDAY_FIELDS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class CreateJustifiedAbsence:
    def __init__(self, repository: CreateJustifiedAbsenceRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        absence_date: date,
        reason: Optional[str],
    ) -> JustifiedAbsence:
        employee = await self.repository.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        schedule = await self.repository.get_schedule(employee_id)
        weekday_field = WEEKDAY_FIELDS[absence_date.weekday()]
        if not schedule or not getattr(schedule, weekday_field):
            raise ValueError("Date is not a scheduled work day")

        if await self.repository.exists(employee_id, absence_date):
            raise ValueError("Justified absence already exists for this date")

        return await self.repository.create(employee_id, absence_date, reason)
