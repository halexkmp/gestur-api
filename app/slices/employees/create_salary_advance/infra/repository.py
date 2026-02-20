from uuid import UUID
from decimal import Decimal
from app.shared.db.models import SalaryAdvance, Employee
from app.slices.employees.create_salary_advance.domain.rules import (
    ensure_monthly_advances_do_not_exceed_salary,
)


class CreateSalaryAdvanceRepository:
    async def create(
        self,
        employee_id: UUID,
        amount: Decimal,
        note: str | None = None,
    ):
        # Ensure employee exists
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            raise ValueError("Employee not found")

        # Enforce domain rule: total advances in current month cannot exceed salary
        await ensure_monthly_advances_do_not_exceed_salary(employee, amount)

        return await SalaryAdvance.create(
            employee=employee,
            amount=amount,
            note=note,
        )
