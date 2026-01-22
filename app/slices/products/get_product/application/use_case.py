from uuid import UUID
from app.slices.products.get_product.infra.repository import GetProductRepository

class GetProduct:
    def __init__(self, repository: GetProductRepository):
        self.repository = repository

    async def execute(self, product_id: UUID):
        return await self.repository.get(product_id)