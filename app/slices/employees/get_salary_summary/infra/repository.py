from uuid import UUID
from decimal import Decimal
from typing import Tuple
from app.shared.db.models import Employee, SalaryAdvance


class GetSalarySummaryRepository:
    async def get_employee_and_month_advances(
        self, employee_id: UUID, month: int, year: int
    ) -> Tuple[Employee, Decimal]:
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            raise ValueError("Employee not found")
        # Sum advances in Python to avoid cross-db function differences
        amounts = await SalaryAdvance.filter(
            employee_id=employee_id, created_at__month=month, created_at__year=year
        ).values_list("amount", flat=True)
        total = sum(Decimal(str(a)) for a in amounts) if amounts else Decimal("0")
        return employee, total
