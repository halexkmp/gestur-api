from datetime import datetime, timezone


class DeviceHeartbeat:
    def execute(self) -> datetime:
        return datetime.now(timezone.utc)
