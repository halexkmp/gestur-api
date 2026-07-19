from typing import Optional
from uuid import UUID

from app.slices.employees.list_my_salary_advances.infra.repository import ListMyAdvancesRepository


class ListMyAdvances:
    def __init__(self, repository: ListMyAdvancesRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ):
        return await self.repository.list(
            employee_id=employee_id,
            month=month,
            year=year,
        )
