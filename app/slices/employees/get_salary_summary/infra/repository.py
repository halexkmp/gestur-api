from uuid import UUID
from decimal import Decimal
from typing import Tuple
from datetime import date
from app.shared.db.models import Employee, SalaryAdvance


class GetSalarySummaryRepository:
    async def get_employee_and_month_advances(
        self, employee_id: UUID, month: int, year: int
    ) -> Tuple[Employee, Decimal]:
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            raise ValueError("Employee not found")

        start = date(year, month, 1)
        if month == 12:
            next_month_first = date(year + 1, 1, 1)
        else:
            next_month_first = date(year, month + 1, 1)

        # Sum advances in Python to avoid cross-db function differences
        amounts = await SalaryAdvance.filter(
            employee_id=employee_id,
            advance_date__gte=start,
            advance_date__lt=next_month_first,
        ).values_list("amount", flat=True)
        total = sum(Decimal(str(a)) for a in amounts) if amounts else Decimal("0")
        return employee, total
