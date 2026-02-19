from uuid import UUID
from datetime import date
from typing import Optional, List
from app.slices.employees.list_salary_advances.infra.repository import ListSalaryAdvancesRepository


class ListSalaryAdvances:
    def __init__(self, repository: ListSalaryAdvancesRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: Optional[UUID] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> List[object]:
        # Default to current month/year if provided partially
        if (month is None) ^ (year is None):
            today = date.today()
            month = month or today.month
            year = year or today.year
        return await self.repository.list(
            employee_id=employee_id,
            month=month,
            year=year,
        )
