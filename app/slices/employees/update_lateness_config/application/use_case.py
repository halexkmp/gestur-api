from datetime import time
from decimal import Decimal
from app.slices.employees.update_lateness_config.infra.repository import UpdateLatenessConfigurationRepository


class UpdateLatenessConfiguration:
    def __init__(self, repository: UpdateLatenessConfigurationRepository):
        self.repository = repository

    async def execute(
        self,
        enabled: bool,
        expected_entrance_time: time,
        tolerance_minutes: int,
        deduction_interval_minutes: int,
        deduction_value: Decimal,
        late_penalty_hours: Decimal,
        monthly_work_hours: int,
    ):
        if tolerance_minutes < 0:
            raise ValueError("tolerance_minutes must be >= 0")
        if deduction_interval_minutes <= 0:
            raise ValueError("deduction_interval_minutes must be > 0")
        if deduction_value < 0:
            raise ValueError("deduction_value must be >= 0")
        if late_penalty_hours < 0 or late_penalty_hours >= 1000:
            raise ValueError("late_penalty_hours must be >= 0 and < 1000")
        if monthly_work_hours <= 0:
            raise ValueError("monthly_work_hours must be > 0")

        return await self.repository.upsert(
            enabled=enabled,
            expected_entrance_time=expected_entrance_time,
            tolerance_minutes=tolerance_minutes,
            deduction_interval_minutes=deduction_interval_minutes,
            deduction_value=deduction_value,
            late_penalty_hours=late_penalty_hours,
            monthly_work_hours=monthly_work_hours,
        )
