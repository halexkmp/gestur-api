from uuid import UUID
from datetime import date
from app.slices.employees.create_salary_advance.infra.repository import CreateSalaryAdvanceRepository

class CreateSalaryAdvance:
    def __init__(self, repository: CreateSalaryAdvanceRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        amount: float,
        paid_at: date | None = None,
        note: str | None = None,
    ):
        return await self.repository.create(
            employee_id=employee_id,
            amount=amount,
            paid_at=paid_at or date.today(),
            note=note,
        )
