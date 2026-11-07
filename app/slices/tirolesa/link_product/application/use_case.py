from uuid import UUID

from app.shared.db.models import TirolesaProduct
from app.slices.tirolesa.link_product.infra.repository import LinkProductRepository


class ProductNotFound(Exception):
    pass


class ProductAlreadyLinked(Exception):
    pass


class LinkProduct:
    def __init__(self, repository: LinkProductRepository):
        self.repository = repository

    async def execute(self, product_id: UUID, passengers_per_unit: int) -> TirolesaProduct:
        if not await self.repository.product_exists(product_id):
            raise ProductNotFound()
        if await self.repository.is_linked(product_id):
            raise ProductAlreadyLinked()
        return await self.repository.create(product_id, passengers_per_unit)
