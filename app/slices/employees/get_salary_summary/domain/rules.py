from datetime import datetime, time, timedelta, timezone
from decimal import Decimal


def _time_of_day_minutes(value: datetime | time) -> float:
    """UTC-normalized minutes since midnight for a datetime or a time value."""
    if isinstance(value, datetime):
        value = value.astimezone(timezone.utc).time() if value.tzinfo else value.time()
    elif value.tzinfo:
        value = value.replace(tzinfo=None)

    return value.hour * 60 + value.minute + value.second / 60


def calculate_daily_delay_minutes(
    entrance_at: datetime, expected_entrance_time: time, utc_offset_minutes: int
) -> int:
    """Minutes entrance_at is later than expected_entrance_time on entrance_at's local
    calendar day, floored at 0.

    Computed as an elapsed-time difference anchored to the local business day, not a
    same-day time-of-day subtraction — a check-in whose UTC clock time is numerically
    earlier than expected_entrance_time (e.g. a local evening arrival that has already
    rolled into the next UTC calendar date) would otherwise wrap to a large negative
    number and clamp to zero instead of reporting the real multi-hour delay.
    """
    offset = timedelta(minutes=utc_offset_minutes)
    local_entrance = entrance_at + offset
    local_day = local_entrance.date()

    local_expected_minutes = (_time_of_day_minutes(expected_entrance_time) + utc_offset_minutes) % 1440
    local_expected = datetime.combine(local_day, time.min, tzinfo=local_entrance.tzinfo) + timedelta(
        minutes=local_expected_minutes
    )

    delay = (local_entrance - local_expected).total_seconds() / 60
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
