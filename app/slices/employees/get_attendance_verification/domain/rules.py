from datetime import date, timedelta

PRESENT = "PRESENT"
JUSTIFIED_ABSENCE = "JUSTIFIED_ABSENCE"
UNJUSTIFIED_ABSENCE = "UNJUSTIFIED_ABSENCE"


def classify_attendance_days(
    scheduled_weekdays: set[int],
    justified_absence_dates: set[date],
    present_dates: set[date],
    period_start: date,
    period_end: date,
) -> list[tuple[date, str]]:
    """Classify every scheduled work day in [period_start, period_end] (inclusive).

    Non-scheduled weekdays are excluded entirely. A justified absence takes priority
    over presence — an employee with both a journey register and a justified absence
    on the same date is still reported as justified, not present.
    """
    days: list[tuple[date, str]] = []
    current = period_start
    while current <= period_end:
        if current.weekday() in scheduled_weekdays:
            if current in justified_absence_dates:
                days.append((current, JUSTIFIED_ABSENCE))
            elif current in present_dates:
                days.append((current, PRESENT))
            else:
                days.append((current, UNJUSTIFIED_ABSENCE))
        current += timedelta(days=1)

    return days
