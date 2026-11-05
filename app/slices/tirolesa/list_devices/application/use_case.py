from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from app.slices.tirolesa.list_devices.infra.repository import ListDevicesRepository

OFFLINE_AFTER = timedelta(minutes=15)


@dataclass(frozen=True)
class DeviceStatus:
    id: UUID
    name: str
    active: bool
    last_seen_at: Optional[datetime]
    offline: bool


class ListDevices:
    def __init__(self, repository: ListDevicesRepository):
        self.repository = repository

    async def execute(self) -> List[DeviceStatus]:
        now = datetime.now(timezone.utc)
        devices = await self.repository.list()
        return [
            DeviceStatus(
                id=device.id,
                name=device.name,
                active=device.active,
                last_seen_at=device.last_seen_at,
                offline=device.active
                and (device.last_seen_at is None or now - device.last_seen_at > OFFLINE_AFTER),
            )
            for device in devices
        ]
