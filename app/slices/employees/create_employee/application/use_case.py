from datetime import date
from uuid import UUID

from app.shared.db.models import Employee, User
from app.slices.employees.create_employee.infra.repository import CreateEmployeeRepository

class CreateEmployee:
    def __init__(self, repository: CreateEmployeeRepository):
        self.repository = repository

    async def execute(
        self,
        name: str,
        pix_key: str | None,
        salary: float,
        active: bool,
        start_date: date,
        user_id: UUID | None = None
    ):
        if user_id is not None:
            user = await User.get_or_none(id=user_id)
            if not user:
                raise ValueError("User not found")
            if await Employee.get_or_none(user_id=user_id):
                raise ValueError("User is already linked to another employee")

        return await self.repository.create(
            name=name,
            pix_key=pix_key,
            salary=salary,
            active=active,
            start_date=start_date,
            user_id=user_id
        )
