from uuid import UUID
from typing import Optional
from datetime import date, datetime, timedelta

from app.shared.db.models import Employee, EmployeeSchedule, JustifiedAbsence, JourneyRegistry, LatenessConfiguration


class GetAttendanceVerificationRepository:
    async def get_employee(self, employee_id: UUID) -> Optional[Employee]:
        return await Employee.get_or_none(id=employee_id)

    async def get_schedule(self, employee_id: UUID) -> Optional[EmployeeSchedule]:
        return await EmployeeSchedule.get_or_none(employee_id=employee_id)

    async def get_justified_absence_dates(self, employee_id: UUID, month: int, year: int) -> set[date]:
        start, next_month_first = _month_range(month, year)
        dates = await JustifiedAbsence.filter(
            employee_id=employee_id,
            absence_date__gte=start,
            absence_date__lt=next_month_first,
        ).values_list("absence_date", flat=True)
        return set(dates)

    async def get_present_dates(self, user_id: UUID, month: int, year: int) -> set[date]:
        start, next_month_first = _month_range(month, year)

        config = await LatenessConfiguration.all().order_by("created_at").first()
        utc_offset_minutes = config.utc_offset_minutes if config else -180

        timestamps = await JourneyRegistry.filter(
            user_id=user_id,
            is_deleted=False,
            timestamp__gte=start,
            timestamp__lt=next_month_first,
        ).values_list("timestamp", flat=True)

        local_offset = timedelta(minutes=utc_offset_minutes)
        present_dates: set[date] = set()
        for ts in timestamps:
            present_dates.add((ts + local_offset).date())
        return present_dates


def _month_range(month: int, year: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    return start, next_month_first
