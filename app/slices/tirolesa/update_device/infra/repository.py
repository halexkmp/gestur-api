from typing import Optional
from uuid import UUID

from app.shared.db.models import TirolesaDevice


class UpdateDeviceRepository:
    async def get(self, device_id: UUID) -> Optional[TirolesaDevice]:
        return await TirolesaDevice.get_or_none(id=device_id)

    async def save(self, device: TirolesaDevice) -> None:
        await device.save(update_fields=["name", "active"])
