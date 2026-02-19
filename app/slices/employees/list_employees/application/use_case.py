from app.slices.employees.list_employees.infra.repository import ListEmployeesRepository
from typing import Optional

class ListEmployees:
    def __init__(self, repository: ListEmployeesRepository):
        self.repository = repository

    async def execute(self, active: Optional[bool] = None):
        return await self.repository.list(active=active)
