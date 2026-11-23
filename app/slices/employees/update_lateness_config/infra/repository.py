from datetime import date, datetime, time, timezone
from decimal import Decimal
from app.shared.db.models import LatenessConfiguration


def _to_utc_time(value: time) -> time:
    """Normalize any time-of-day (naive or carrying any UTC offset) to true UTC.

    A naive value is assumed to already be UTC. A value carrying a non-UTC
    offset (e.g. a client submitting "08:00:00-03:00") must be converted, not
    just have its offset dropped — otherwise the wall-clock hour would be
    silently misread as UTC, shifting delay calculations by the offset amount.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return datetime.combine(date(2000, 1, 1), value).astimezone(timezone.utc).timetz()


class UpdateLatenessConfigurationRepository:
    async def upsert(
        self,
        enabled: bool,
        expected_entrance_time: time,
        tolerance_minutes: int,
        deduction_interval_minutes: int,
        deduction_value: Decimal,
        late_penalty_hours: Decimal,
        monthly_work_hours: int,
    ) -> LatenessConfiguration:
        # Column is TIMETZ (matching the migration-seeded CURRENT_TIME row); always
        # bind a UTC-normalized value regardless of what offset the request carried.
        expected_entrance_time = _to_utc_time(expected_entrance_time)

        config = await LatenessConfiguration.all().order_by("created_at").first()
        if not config:
            return await LatenessConfiguration.create(
                enabled=enabled,
                expected_entrance_time=expected_entrance_time,
                tolerance_minutes=tolerance_minutes,
                deduction_interval_minutes=deduction_interval_minutes,
                deduction_value=deduction_value,
                late_penalty_hours=late_penalty_hours,
                monthly_work_hours=monthly_work_hours,
            )

        config.enabled = enabled
        config.expected_entrance_time = expected_entrance_time
        config.tolerance_minutes = tolerance_minutes
        config.deduction_interval_minutes = deduction_interval_minutes
        config.deduction_value = deduction_value
        config.late_penalty_hours = late_penalty_hours
        config.monthly_work_hours = monthly_work_hours
        await config.save()
        return config
