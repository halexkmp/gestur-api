from app.shared.db.models import TirolesaDevice


class CreateDeviceRepository:
    async def create(self, name: str, api_key_hash: str) -> TirolesaDevice:
        return await TirolesaDevice.create(name=name, api_key_hash=api_key_hash)
