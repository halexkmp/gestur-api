from typing import List

from app.shared.db.models import TirolesaDevice


class ListDevicesRepository:
    async def list(self) -> List[TirolesaDevice]:
        return await TirolesaDevice.all().order_by("name")
