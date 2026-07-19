from datetime import datetime, time, timezone
from decimal import Decimal


def _time_of_day_minutes(value: datetime | time) -> float:
    """UTC-normalized minutes since midnight for a datetime or a time value."""
    if isinstance(value, datetime):
        value = value.astimezone(timezone.utc).time() if value.tzinfo else value.time()
    elif value.tzinfo:
        value = value.replace(tzinfo=None)

    return value.hour * 60 + value.minute + value.second / 60


def calculate_daily_delay_minutes(entrance_at: datetime, expected_entrance_time: time) -> int:
    """Minutes entrance_at is later than expected_entrance_time, floored at 0."""
    delay = _time_of_day_minutes(entrance_at) - _time_of_day_minutes(expected_entrance_time)
    return max(0, round(delay))


def is_late(delay_minutes: int, tolerance_minutes: int) -> bool:
    return delay_minutes > tolerance_minutes


def calculate_deduction(
    delay_minutes: int,
    deduction_interval_minutes: int,
    deduction_value: Decimal,
) -> Decimal:
    """floor(delay_minutes / deduction_interval_minutes) * deduction_value.

    Guards against a zero/negative interval (e.g. the disabled bootstrapped
    config row) by returning zero instead of dividing by zero.
    """
    if deduction_interval_minutes <= 0:
        return Decimal("0")

    blocks = delay_minutes // deduction_interval_minutes
    return blocks * deduction_value
