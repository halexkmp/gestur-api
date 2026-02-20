from datetime import date
from typing import Optional, List
from app.slices.employees.list_salary_advances.infra.repository import ListSalaryAdvancesRepository


class ListSalaryAdvances:
    def __init__(self, repository: ListSalaryAdvancesRepository):
        self.repository = repository

    async def execute(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ):
        if (month is None) ^ (year is None):
            today = date.today()
            month = month or today.month
            year = year or today.year
        return await self.repository.list(
            month=month,
            year=year,
        )
