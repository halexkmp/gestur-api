from datetime import datetime, timedelta

MAX_FUTURE_DRIFT = timedelta(minutes=5)
MAX_START_AGE = timedelta(days=7)


def is_clock_suspect(start: datetime, end: datetime, now: datetime) -> bool:
    """A trip whose times cannot be trusted. It is kept, but placed by when it arrived."""
    return (
        start > now + MAX_FUTURE_DRIFT
        or end > now + MAX_FUTURE_DRIFT
        or start < now - MAX_START_AGE
        or end <= start
    )
