from uuid import UUID
from app.shared.db.models import Employee

class DeleteEmployeeRepository:
    async def delete(self, employee_id: UUID) -> bool:
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            return False
        await employee.delete()
        return True
