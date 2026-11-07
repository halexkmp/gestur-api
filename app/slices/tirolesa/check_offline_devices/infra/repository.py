from datetime import datetime

from app.shared.db.models import TirolesaDevice


class CheckOfflineDevicesRepository:
    async def mark_offline_if_not_seen_since(self, cutoff: datetime) -> int:
        return await TirolesaDevice.filter(
            active=True,
            offline=False,
            last_seen_at__lt=cutoff,
        ).update(offline=True)
