from datetime import date

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
        start_date: date
    ):
        return await self.repository.create(
            name=name,
            pix_key=pix_key,
            salary=salary,
            active=active,
            start_date=start_date
        )
