from datetime import date
from uuid import UUID
from typing import Optional
from app.slices.employees.update_employee.infra.repository import UpdateEmployeeRepository

class UpdateEmployee:
    def __init__(self, repository: UpdateEmployeeRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        name: Optional[str] = None,
        pix_key: Optional[str] = None,
        salary: Optional[float] = None,
        active: Optional[bool] = None,
        start_date: Optional[date] = None
    ):
        updated = await self.repository.update(
            employee_id=employee_id,
            name=name,
            pix_key=pix_key,
            salary=salary,
            active=active,
            start_date=start_date
        )
        if not updated:
            raise ValueError("Employee not found")
        return updated
