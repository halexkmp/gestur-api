from uuid import UUID
from decimal import Decimal
from typing import List, Optional, Tuple
from datetime import date, datetime
from app.shared.db.models import Employee, SalaryAdvance, JourneyRegistry, LatenessConfiguration


class GetMySalarySummaryRepository:
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

    async def get_lateness_configuration(self) -> Optional[LatenessConfiguration]:
        return await LatenessConfiguration.all().order_by("created_at").first()

    async def get_journey_timestamps(
        self, user_id: UUID, month: int, year: int
    ) -> List[datetime]:
        start = date(year, month, 1)
        if month == 12:
            next_month_first = date(year + 1, 1, 1)
        else:
            next_month_first = date(year, month + 1, 1)

        return await JourneyRegistry.filter(
            user_id=user_id,
            is_deleted=False,
            timestamp__gte=start,
            timestamp__lt=next_month_first,
        ).order_by("timestamp").values_list("timestamp", flat=True)
