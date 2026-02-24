from uuid import UUID
from app.shared.db.models import Employee

class GetEmployeeRepository:
    async def get(self, employee_id: UUID):
        return await Employee.get_or_none(id=employee_id)
