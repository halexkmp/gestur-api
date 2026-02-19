from uuid import UUID
from datetime import date
from app.shared.db.models import SalaryAdvance, Employee


class CreateSalaryAdvanceRepository:
    async def create(
        self,
        employee_id: UUID,
        amount: float,
        paid_at: date,
        note: str | None = None,
    ):
        # Ensure employee exists
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            raise ValueError("Employee not found")
        return await SalaryAdvance.create(
            employee=employee,
            amount=amount,
            paid_at=paid_at,
            note=note,
        )
