from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from app.shared.db.models import LatenessConfiguration
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
        month: int | None = None,
        year: int | None = None,
    ) -> List[dict]:
        # Default month/year to current when not provided
        today = date.today()
        month = month or today.month
        year = year or today.year

        employees = await self.repository.get_all_employees()
        if not employees:
            return []

        employee_ids = [employee.id for employee in employees]
        advances_by_employee = await self.repository.get_month_advances_bulk(
            employee_ids=employee_ids, month=month, year=year
        )

        # Lateness config is a single global row — fetched once regardless of employee count.
        config = await self.repository.get_lateness_configuration()

        # Only bulk-fetch journeys when lateness is actually enabled, to avoid an
        # unnecessary query when every employee's lateness fields are zero anyway.
        user_ids = [employee.user_id for employee in employees if employee.user_id is not None]
        timestamps_by_user = (
            await self.repository.get_journey_timestamps_bulk(user_ids=user_ids, month=month, year=year)
            if user_ids and config and config.enabled
            else {}
        )

        results: List[dict] = []
        for employee in employees:
            employee_advances = advances_by_employee.get(employee.id, [])
            advances_total = sum(
                (Decimal(advance.amount) for advance in employee_advances), Decimal("0")
            )

            late_delay_minutes, late_days_count, late_deduction_total = self._calculate_lateness(
                employee_user_id=employee.user_id,
                config=config,
                timestamps=timestamps_by_user.get(employee.user_id, []) if employee.user_id else [],
            )

            gross_salary = Decimal(employee.salary)
            net_salary = gross_salary - advances_total - late_deduction_total

            results.append(
                {
                    "employee_id": employee.id,
                    "month": month,
                    "year": year,
                    "gross_salary": gross_salary,
                    "advances_total": advances_total,
                    "advances": [
                        {
                            "id": advance.id,
                            "amount": Decimal(advance.amount),
                            "advance_date": advance.advance_date,
                            "note": advance.note,
                        }
                        for advance in employee_advances
                    ],
                    "late_delay_minutes": late_delay_minutes,
                    "late_days_count": late_days_count,
                    "late_deduction_total": late_deduction_total,
                    "net_salary": net_salary,
                }
            )

        return results

    def _calculate_lateness(
        self,
        employee_user_id: UUID | None,
        config: Optional[LatenessConfiguration],
        timestamps: List[datetime],
    ) -> tuple[int, int, Decimal]:
        if employee_user_id is None:
            return 0, 0, Decimal("0")

        if not config or not config.enabled:
            return 0, 0, Decimal("0")

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
