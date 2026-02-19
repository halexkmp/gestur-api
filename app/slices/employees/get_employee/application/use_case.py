from uuid import UUID
from app.slices.employees.get_employee.infra.repository import GetEmployeeRepository

class GetEmployee:
    def __init__(self, repository: GetEmployeeRepository):
        self.repository = repository

    async def execute(self, employee_id: UUID):
        employee = await self.repository.get(employee_id=employee_id)
        if not employee:
            raise ValueError("Employee not found")
        return employee
