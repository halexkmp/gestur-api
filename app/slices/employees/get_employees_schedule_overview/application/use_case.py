from uuid import UUID
from typing import Optional
from datetime import date, timedelta

from app.slices.employees.get_employees_schedule_overview.infra.repository import (
    GetEmployeesScheduleOverviewRepository,
)
from app.slices.employees.get_attendance_verification.domain.rules import classify_attendance_days

WEEKDAY_FIELDS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class GetEmployeesScheduleOverview:
    def __init__(self, repository: GetEmployeesScheduleOverviewRepository):
        self.repository = repository

    async def execute(
        self,
        employee_ids: Optional[list[UUID]],
        month: Optional[int],
        year: Optional[int],
    ) -> list[dict]:
        today = date.today()
        month = month or today.month
        year = year or today.year

        employees = await self.repository.get_employees(employee_ids)
        if not employees:
            return []

        schedules_by_employee = await self.repository.get_schedules([employee.id for employee in employees])
        employees = [employee for employee in employees if employee.id in schedules_by_employee]
        if not employees:
            return []

        justified_absences_by_employee = await self.repository.get_justified_absence_dates_bulk(
            [employee.id for employee in employees], month, year
        )

        user_ids = [employee.user_id for employee in employees if employee.user_id is not None]
        present_dates_by_user = await self.repository.get_present_dates_bulk(user_ids, month, year) if user_ids else {}

        items = []
        for employee in employees:
            schedule = schedules_by_employee[employee.id]

            if employee.user_id is None or not employee.active:
                items.append(self._build_item(employee.id, schedule, month, year, [], 0))
                continue

            period_start = date(year, month, 1)
            if month == 12:
                period_end = date(year, 12, 31)
            else:
                period_end = date(year, month + 1, 1) - timedelta(days=1)

            if period_start < employee.start_date:
                period_start = employee.start_date
            if period_end > today:
                period_end = today

            if period_start > period_end:
                items.append(self._build_item(employee.id, schedule, month, year, [], 0))
                continue

            scheduled_weekdays = {
                index for index, field in enumerate(WEEKDAY_FIELDS) if getattr(schedule, field)
            }

            classified_days = classify_attendance_days(
                scheduled_weekdays=scheduled_weekdays,
                justified_absence_dates=justified_absences_by_employee.get(employee.id, set()),
                present_dates=present_dates_by_user.get(employee.user_id, set()),
                period_start=period_start,
                period_end=period_end,
            )

            days = [{"date": day, "status": status} for day, status in classified_days]
            unjustified_absence_count = sum(1 for _, status in classified_days if status == "UNJUSTIFIED_ABSENCE")

            items.append(self._build_item(employee.id, schedule, month, year, days, unjustified_absence_count))

        return items

    def _build_item(self, employee_id, schedule, month, year, days, unjustified_absence_count) -> dict:
        return {
            "employee_id": employee_id,
            "monday": schedule.monday,
            "tuesday": schedule.tuesday,
            "wednesday": schedule.wednesday,
            "thursday": schedule.thursday,
            "friday": schedule.friday,
            "saturday": schedule.saturday,
            "sunday": schedule.sunday,
            "month": month,
            "year": year,
            "days": days,
            "unjustified_absence_count": unjustified_absence_count,
        }
