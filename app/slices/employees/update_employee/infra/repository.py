from datetime import date
from typing import Optional
from uuid import UUID
from app.shared.db.models import Employee

class UpdateEmployeeRepository:
    async def update(
        self,
        employee_id: UUID,
        name: Optional[str] = None,
        pix_key: Optional[str] = None,
        salary: Optional[float] = None,
        active: Optional[bool] = None,
        start_date: Optional[date] = None
    ):
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            return None
        if name is not None:
            employee.name = name
        if pix_key is not None:
            employee.pix_key = pix_key
        if salary is not None:
            employee.salary = salary
        if active is not None:
            employee.active = active
        if start_date is not None:
            employee.start_date = start_date
        await employee.save()
        return employee
