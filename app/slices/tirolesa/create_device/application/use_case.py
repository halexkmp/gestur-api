from app.shared.db.models import TirolesaDevice
from app.shared.security.device_auth import generate_device_key
from app.slices.tirolesa.create_device.infra.repository import CreateDeviceRepository


class CreateDevice:
    def __init__(self, repository: CreateDeviceRepository):
        self.repository = repository

    async def execute(self, name: str) -> tuple[TirolesaDevice, str]:
        plain_key, key_hash = generate_device_key()
        device = await self.repository.create(name, key_hash)
        return device, plain_key
