from uuid import UUID
from typing import Optional

from app.shared.db.models import Employee, EmployeeSchedule


class GetMyEmployeeScheduleRepository:
    async def get_employee(self, employee_id: UUID) -> Optional[Employee]:
        return await Employee.get_or_none(id=employee_id)

    async def get_schedule(self, employee_id: UUID) -> Optional[EmployeeSchedule]:
        return await EmployeeSchedule.get_or_none(employee_id=employee_id)
