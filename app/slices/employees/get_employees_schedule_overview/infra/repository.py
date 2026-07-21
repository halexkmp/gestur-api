from uuid import UUID
from typing import Optional
from datetime import date, timedelta

from app.shared.db.models import Employee, EmployeeSchedule, JustifiedAbsence, JourneyRegistry, LatenessConfiguration


class GetEmployeesScheduleOverviewRepository:
    async def get_employees(self, employee_ids: Optional[list[UUID]]) -> list[Employee]:
        if employee_ids:
            return await Employee.filter(id__in=employee_ids)
        return await Employee.all()

    async def get_schedules(self, employee_ids: list[UUID]) -> dict[UUID, EmployeeSchedule]:
        schedules = await EmployeeSchedule.filter(employee_id__in=employee_ids)
        return {schedule.employee_id: schedule for schedule in schedules}

    async def get_justified_absence_dates_bulk(
        self, employee_ids: list[UUID], month: int, year: int
    ) -> dict[UUID, set[date]]:
        start, next_month_first = _month_range(month, year)
        rows = await JustifiedAbsence.filter(
            employee_id__in=employee_ids,
            absence_date__gte=start,
            absence_date__lt=next_month_first,
        ).values_list("employee_id", "absence_date")

        dates_by_employee: dict[UUID, set[date]] = {}
        for employee_id, absence_date in rows:
            dates_by_employee.setdefault(employee_id, set()).add(absence_date)
        return dates_by_employee

    async def get_present_dates_bulk(
        self, user_ids: list[UUID], month: int, year: int
    ) -> dict[UUID, set[date]]:
        start, next_month_first = _month_range(month, year)

        config = await LatenessConfiguration.all().order_by("created_at").first()
        utc_offset_minutes = config.utc_offset_minutes if config else -180
        local_offset = timedelta(minutes=utc_offset_minutes)

        rows = await JourneyRegistry.filter(
            user_id__in=user_ids,
            is_deleted=False,
            timestamp__gte=start,
            timestamp__lt=next_month_first,
        ).values_list("user_id", "timestamp")

        dates_by_user: dict[UUID, set[date]] = {}
        for user_id, timestamp in rows:
            dates_by_user.setdefault(user_id, set()).add((timestamp + local_offset).date())
        return dates_by_user


def _month_range(month: int, year: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    return start, next_month_first
