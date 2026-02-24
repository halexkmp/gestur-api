from uuid import UUID
from app.slices.employees.delete_employee.infra.repository import DeleteEmployeeRepository

class DeleteEmployee:
    def __init__(self, repository: DeleteEmployeeRepository):
        self.repository = repository

    async def execute(self, employee_id: UUID) -> bool:
        return await self.repository.delete(employee_id)
