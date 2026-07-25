from uuid import UUID
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import date, datetime
from app.shared.db.models import Employee, SalaryAdvance, JourneyRegistry, LatenessConfiguration


class GetSalarySummaryRepository:
    async def get_all_employees(self) -> List[Employee]:
        return await Employee.all()

    async def get_month_advances_bulk(
        self, employee_ids: List[UUID], month: int, year: int
    ) -> Dict[UUID, List[SalaryAdvance]]:
        start, next_month_first = _month_range(month, year)

        advances = await SalaryAdvance.filter(
            employee_id__in=employee_ids,
            advance_date__gte=start,
            advance_date__lt=next_month_first,
        ).order_by("advance_date")

        advances_by_employee: Dict[UUID, List[SalaryAdvance]] = {}
        for advance in advances:
            advances_by_employee.setdefault(advance.employee_id, []).append(advance)
        return advances_by_employee

    async def get_lateness_configuration(self) -> Optional[LatenessConfiguration]:
        return await LatenessConfiguration.all().order_by("created_at").first()

    async def get_journey_timestamps_bulk(
        self, user_ids: List[UUID], month: int, year: int
    ) -> Dict[UUID, List[datetime]]:
        start, next_month_first = _month_range(month, year)

        rows = await JourneyRegistry.filter(
            user_id__in=user_ids,
            is_deleted=False,
            timestamp__gte=start,
            timestamp__lt=next_month_first,
        ).order_by("timestamp").values_list("user_id", "timestamp")

        timestamps_by_user: Dict[UUID, List[datetime]] = {}
        for user_id, timestamp in rows:
            timestamps_by_user.setdefault(user_id, []).append(timestamp)
        return timestamps_by_user


def _month_range(month: int, year: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    return start, next_month_first
