from uuid import UUID
from datetime import date, timedelta

from app.slices.employees.get_attendance_verification.infra.repository import GetAttendanceVerificationRepository
from app.slices.employees.get_attendance_verification.domain.rules import classify_attendance_days

WEEKDAY_FIELDS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class GetAttendanceVerification:
    def __init__(self, repository: GetAttendanceVerificationRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        month: int | None = None,
        year: int | None = None,
    ):
        today = date.today()
        month = month or today.month
        year = year or today.year

        employee = await self.repository.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        empty_result = {
            "employee_id": employee.id,
            "month": month,
            "year": year,
            "days": [],
            "unjustified_absence_count": 0,
        }

        schedule = await self.repository.get_schedule(employee_id)
        if not schedule:
            return empty_result

        # FR-016: presence can never be determined without a linked user account.
        if employee.user_id is None:
            return empty_result

        # FR-011: no deactivation timestamp exists, so a currently-inactive employee
        # excludes their entire requested period rather than just the days after
        # deactivation.
        if not employee.active:
            return empty_result

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
            return empty_result

        scheduled_weekdays = {
            index for index, field in enumerate(WEEKDAY_FIELDS) if getattr(schedule, field)
        }

        justified_absence_dates = await self.repository.get_justified_absence_dates(employee_id, month, year)
        present_dates = await self.repository.get_present_dates(employee.user_id, month, year)

        classified_days = classify_attendance_days(
            scheduled_weekdays=scheduled_weekdays,
            justified_absence_dates=justified_absence_dates,
            present_dates=present_dates,
            period_start=period_start,
            period_end=period_end,
        )

        days = [{"date": day, "status": status} for day, status in classified_days]
        unjustified_absence_count = sum(1 for _, status in classified_days if status == "UNJUSTIFIED_ABSENCE")

        return {
            "employee_id": employee.id,
            "month": month,
            "year": year,
            "days": days,
            "unjustified_absence_count": unjustified_absence_count,
        }
