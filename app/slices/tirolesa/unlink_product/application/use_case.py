from uuid import UUID

from app.slices.tirolesa.unlink_product.infra.repository import UnlinkProductRepository


class UnlinkProduct:
    def __init__(self, repository: UnlinkProductRepository):
        self.repository = repository

    async def execute(self, tirolesa_product_id: UUID) -> bool:
        return await self.repository.delete(tirolesa_product_id)
