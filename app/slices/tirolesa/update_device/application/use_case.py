from typing import Optional
from uuid import UUID

from app.shared.db.models import TirolesaDevice
from app.slices.tirolesa.update_device.infra.repository import UpdateDeviceRepository


class UpdateDevice:
    def __init__(self, repository: UpdateDeviceRepository):
        self.repository = repository

    async def execute(
        self,
        device_id: UUID,
        name: Optional[str],
        active: Optional[bool],
    ) -> TirolesaDevice:
        device = await self.repository.get(device_id)
        if device is None:
            raise ValueError("Device not found")
        if name is not None:
            device.name = name
        if active is not None:
            device.active = active
        await self.repository.save(device)
        return device
