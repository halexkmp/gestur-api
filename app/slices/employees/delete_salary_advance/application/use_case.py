from uuid import UUID
from app.slices.employees.delete_salary_advance.infra.repository import DeleteSalaryAdvanceRepository

class DeleteSalaryAdvance:
    def __init__(self, repository: DeleteSalaryAdvanceRepository):
        self.repository = repository

    async def execute(self, advance_id: UUID) -> bool:
        return await self.repository.delete(advance_id)
