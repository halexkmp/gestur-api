from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.slices.employees.get_salary_summary.infra.repository import GetSalarySummaryRepository
from app.slices.employees.get_salary_summary.domain.rules import (
    calculate_daily_delay_minutes,
    is_late,
    calculate_deduction,
)


class GetSalarySummary:
    def __init__(self, repository: GetSalarySummaryRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        month: int | None = None,
        year: int | None = None,
    ):
        # Default month/year to current when not provided
        today = date.today()
        month = month or today.month
        year = year or today.year

        employee, advances_total = await self.repository.get_employee_and_month_advances(
            employee_id=employee_id,
            month=month,
            year=year,
        )
        # Ensure Decimal math and round to 2 decimal places for money
        salary: Decimal = Decimal(employee.salary)
        advances: Decimal = Decimal(advances_total)

        late_delay_minutes, late_days_count, late_deduction_total = await self._calculate_lateness(
            employee_user_id=employee.user_id,
            month=month,
            year=year,
        )

        net = salary - advances - late_deduction_total
        return {
            "employee_id": employee.id,
            "month": month,
            "year": year,
            "gross_salary": salary,
            "advances_total": advances,
            "late_delay_minutes": late_delay_minutes,
            "late_days_count": late_days_count,
            "late_deduction_total": late_deduction_total,
            "net_salary": net,
        }

    async def _calculate_lateness(
        self,
        employee_user_id: UUID | None,
        month: int,
        year: int,
    ) -> tuple[int, int, Decimal]:
        if employee_user_id is None:
            return 0, 0, Decimal("0")

        config = await self.repository.get_lateness_configuration()
        if not config or not config.enabled:
            return 0, 0, Decimal("0")

        timestamps = await self.repository.get_journey_timestamps(
            user_id=employee_user_id, month=month, year=year
        )

        # Earliest check-in per calendar day is that day's entrance. Bucket by the
        # configured local day, not the UTC day the timestamp is stored in — a
        # check-in near local midnight can carry a different UTC calendar date,
        # which would otherwise misattribute it to the wrong business day.
        local_offset = timedelta(minutes=config.utc_offset_minutes)
        earliest_by_day: dict[date, datetime] = {}
        for ts in timestamps:
            day = (ts + local_offset).date()
            if day not in earliest_by_day or ts < earliest_by_day[day]:
                earliest_by_day[day] = ts

        total_delay_minutes = 0
        late_days_count = 0
        total_deduction = Decimal("0")

        for entrance_at in earliest_by_day.values():
            delay_minutes = calculate_daily_delay_minutes(
                entrance_at, config.expected_entrance_time, config.utc_offset_minutes
            )
            if not is_late(delay_minutes, config.tolerance_minutes):
                continue

            late_days_count += 1
            total_delay_minutes += delay_minutes
            total_deduction += calculate_deduction(
                delay_minutes, config.deduction_interval_minutes, Decimal(config.deduction_value)
            )

        return total_delay_minutes, late_days_count, total_deduction
