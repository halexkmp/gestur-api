from datetime import date
from uuid import UUID
from typing import Optional
from app.shared.db.models import Employee, User
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
        start_date: Optional[date] = None,
        user_id: Optional[UUID] = None,
        clear_user: bool = False
    ):
        if not clear_user and user_id is not None:
            user = await User.get_or_none(id=user_id)
            if not user:
                raise ValueError("User not found")
            if await Employee.exclude(id=employee_id).get_or_none(user_id=user_id):
                raise ValueError("User is already linked to another employee")

        updated = await self.repository.update(
            employee_id=employee_id,
            name=name,
            pix_key=pix_key,
            salary=salary,
            active=active,
            start_date=start_date,
            user_id=user_id,
            clear_user=clear_user
        )
        if not updated:
            raise ValueError("Employee not found")
        return updated
