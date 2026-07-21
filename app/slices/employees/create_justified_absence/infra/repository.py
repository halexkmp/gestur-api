from uuid import UUID
from datetime import date
from typing import Optional

from app.shared.db.models import Employee, EmployeeSchedule, JustifiedAbsence


class CreateJustifiedAbsenceRepository:
    async def get_employee(self, employee_id: UUID) -> Optional[Employee]:
        return await Employee.get_or_none(id=employee_id)

    async def get_schedule(self, employee_id: UUID) -> Optional[EmployeeSchedule]:
        return await EmployeeSchedule.get_or_none(employee_id=employee_id)

    async def exists(self, employee_id: UUID, absence_date: date) -> bool:
        return await JustifiedAbsence.filter(employee_id=employee_id, absence_date=absence_date).exists()

    async def create(self, employee_id: UUID, absence_date: date, reason: Optional[str]) -> JustifiedAbsence:
        return await JustifiedAbsence.create(
            employee_id=employee_id,
            absence_date=absence_date,
            reason=reason,
        )
