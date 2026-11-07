from datetime import datetime, timedelta, timezone

from app.slices.tirolesa.check_offline_devices.infra.repository import CheckOfflineDevicesRepository

OFFLINE_AFTER = timedelta(minutes=15)


class CheckOfflineDevices:
    def __init__(self, repository: CheckOfflineDevicesRepository):
        self.repository = repository

    async def execute(self) -> int:
        cutoff = datetime.now(timezone.utc) - OFFLINE_AFTER
        return await self.repository.mark_offline_if_not_seen_since(cutoff)
