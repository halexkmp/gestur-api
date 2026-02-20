from decimal import Decimal
from uuid import UUID
from app.slices.employees.create_salary_advance.infra.repository import CreateSalaryAdvanceRepository

class CreateSalaryAdvance:
    def __init__(self, repository: CreateSalaryAdvanceRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        amount: Decimal,
        note: str | None = None,
    ):
        return await self.repository.create(
            employee_id=employee_id,
            amount=amount,
            note=note,
        )
